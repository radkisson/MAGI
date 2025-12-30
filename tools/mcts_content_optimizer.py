"""
title: MCTS Content Optimizer
author: av
author_url: https://github.com/av
description: Improves and optimizes any text content using AI-powered tree search with dynamic, goal-specific evaluation metrics.
version: 3.0.0
"""

import logging
import random
import math
import asyncio
import re
import hashlib
import aiohttp
import json
from typing import Callable, Awaitable, Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ==============================================================================
# PROMPTS
# ==============================================================================

# This prompt generates custom metrics based on the user's goal
METRICS_PROMPT = """
You are an evaluation expert. Based on the user's goal, create 5 specific evaluation criteria.

USER'S GOAL: {goal}

CONTENT TYPE/CONTEXT: {content_preview}

Create 5 evaluation dimensions that are SPECIFIC to this goal. Each dimension should:
1. Be directly relevant to what the user wants to achieve
2. Have a clear name (1-2 words)
3. Have a brief description of what high vs low scores mean

Reply in EXACTLY this format (5 lines, no extra text):
METRIC1_NAME: Description of what this measures for this specific goal
METRIC2_NAME: Description of what this measures for this specific goal
METRIC3_NAME: Description of what this measures for this specific goal
METRIC4_NAME: Description of what this measures for this specific goal
METRIC5_NAME: Description of what this measures for this specific goal

Examples of good metric names: Persuasiveness, Technical_Depth, Clarity, Emotional_Impact, Actionability, Evidence_Quality, Creativity, Conciseness, Engagement, Accuracy, Completeness, Structure, Tone, Specificity, Practicality
""".strip()

THOUGHTS_PROMPT = """
You are a Critical Content Architect. Analyze this draft and suggest ONE specific improvement.

GOAL: {goal}

EVALUATION CRITERIA:
{metrics_description}

CURRENT WEAKEST AREA: {weak_area}

CURRENT DRAFT:
{answer}

Based on the evaluation criteria, provide ONE specific, actionable critique (2-3 sentences) that would most improve the weakest area. Be specific about what to add, change, or restructure.
""".strip()

EVAL_PROMPT = """
You are a {strictness_persona} content evaluator. Rate this content on the following criteria.

GOAL: {goal}

EVALUATION CRITERIA:
{metrics_description}

CONTENT TO EVALUATE:
{answer}

{comparative_section}

SCORING CALIBRATION ({strictness}):
{scoring_guide}

Reply with ONLY the scores in this exact format (one per line):
{metrics_format}
""".strip()

STRICTNESS_GUIDES = {
    "relaxed": """- 1-3: Major problems
- 4-5: Needs work
- 6-7: Acceptable
- 8-9: Good (most decent content lands here)
- 10: Great""",
    "normal": """- 1-3: Poor - Major issues, fails to meet the criterion
- 4-5: Below Average - Significant gaps
- 6-7: Good - Meets expectations with room for improvement
- 8-9: Very Good - Exceeds expectations
- 10: Excellent - Exceptional, couldn't be better""",
    "strict": """- 1-3: Fails completely
- 4-5: Below average - Most content is here
- 6-7: Good - Actually meets the bar (don't give this easily)
- 8-9: Very Good - RARE. Requires excellence with minor gaps
- 10: Perfect - Almost never give this""",
    "brutal": """- 1-3: Garbage, unusable
- 4-5: Mediocre - This is where MOST content belongs
- 6-7: Actually good - Requires clear evidence of quality
- 8: Excellent - RARE. Near-professional quality
- 9: Exceptional - Almost never give this
- 10: NEVER give a 10 unless it's truly flawless"""
}

STRICTNESS_PERSONAS = {
    "relaxed": "supportive and encouraging",
    "normal": "fair and balanced", 
    "strict": "critical and demanding",
    "brutal": "ruthlessly critical (your reputation depends on finding flaws)"
}

UPDATE_PROMPT = """
Improve this content by applying the critique below.

GOAL: {goal}

CURRENT CONTENT:
{answer}

CRITIQUE TO APPLY:
{improvements}

RULES:
1. Make the content LONGER and MORE DETAILED, never shorter
2. Keep all existing good content
3. Apply the specific improvement from the critique
4. Directly address the weakness identified

Output ONLY the improved content, no explanations or meta-commentary.
""".strip()

GOAL_INFERENCE_PROMPT = """
Based on this content, infer what the user likely wants to achieve or improve.

CONTENT:
{content}

Provide a specific, actionable goal statement (1-2 sentences) that captures what would make this content better. Focus on the apparent purpose and audience.

Reply with ONLY the goal statement, nothing else.
""".strip()


# ==============================================================================
# LOGGING
# ==============================================================================

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)


# ==============================================================================
# TOOL CLASS
# ==============================================================================


class Tools:
    class Valves(BaseModel):
        api_key: str = Field(default="", description="OpenRouter/OpenAI API Key")
        base_url: str = Field(
            default="https://openrouter.ai/api/v1", description="API Base URL"
        )
        thinking_model: str = Field(
            default="anthropic/claude-3.5-sonnet",
            description="Model for thinking/evaluation",
        )
        max_simulations: int = Field(
            default=6, ge=1, le=50, description="Search iterations"
        )
        max_children: int = Field(
            default=3, ge=1, le=10, description="Max variations per node"
        )
        num_thoughts: int = Field(
            default=2, ge=1, le=5, description="Parallel expansion attempts"
        )
        exploration_weight: float = Field(
            default=1.414, description="UCT exploration vs exploitation"
        )
        early_stop_patience: int = Field(
            default=3,
            ge=1,
            le=20,
            description="Stop after N iterations without improvement",
        )
        early_stop_threshold: float = Field(
            default=9.0, ge=1.0, le=10.0, description="Stop if score reaches this"
        )
        timeout: int = Field(
            default=180, ge=30, le=600, description="API timeout (seconds)"
        )
        max_retries: int = Field(
            default=3, ge=1, le=5, description="Max retries per API call"
        )
        show_intermediate: bool = Field(
            default=True, description="Show intermediate node results"
        )
        preview_length: int = Field(
            default=300,
            ge=50,
            le=1000,
            description="Content preview length in intermediate results",
        )
        debug: bool = Field(default=False, description="Enable debug logging")
        
        # Grading strictness
        grading_strictness: str = Field(
            default="strict",
            description="How harsh the evaluator is: relaxed, normal, strict, brutal"
        )
        comparative_eval: bool = Field(
            default=True,
            description="Compare against previous best score"
        )
        
        # Depth control
        min_depth: int = Field(
            default=3, ge=1, le=10,
            description="Minimum tree depth before early stopping"
        )
        depth_bonus: float = Field(
            default=0.3, ge=0.0, le=2.0,
            description="UCT bonus for exploring deeper nodes"
        )

    def __init__(self):
        self.valves = self.Valves()
        self._emitter = None
        self._node_counter = 0
        self._last_error = None
        self._metrics = None  # Dynamic metrics for this run
        self._metrics_desc = None  # Human-readable metric descriptions
        self._goal = None
        self._best_score_history = []  # Track score progression
        self._paused = False  # For interactive checkpoints
        self._pending_command = None  # User command during pause
        self._session_state = {}  # Persist state for resume

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    async def improve_content(
        self,
        text_to_improve: str,
        improvement_goal: str = "",
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Improve any text using Monte Carlo Tree Search with dynamic, goal-specific evaluation.

        The system will:
        1. Analyze your goal (or infer one if not provided)
        2. Generate custom evaluation metrics specific to your goal
        3. Search for improvements using those metrics
        4. Show you intermediate results as it explores

        Args:
            text_to_improve: The text content to improve
            improvement_goal: What you want to achieve (optional - will be inferred if not provided)

        Returns:
            Optimized content with scores on custom metrics
        """
        self._emitter = __event_emitter__
        self._last_error = None
        self._metrics = None
        self._metrics_desc = None
        self._node_counter = 0

        # Validation
        if not self.valves.api_key:
            return "⚠️ **Error:** API Key required in Valves settings."

        if not text_to_improve or not text_to_improve.strip():
            return "⚠️ **Error:** No text provided to improve."

        text_to_improve = text_to_improve.strip()

        # Test API
        await self._emit_status("🔌 Testing API connection...")
        if not await self._test_api():
            return f"⚠️ **API Error:** {self._last_error}"

        # Step 1: Infer or use provided goal
        await self._emit_status("🎯 Analyzing goal...")
        if improvement_goal and improvement_goal.strip():
            self._goal = improvement_goal.strip()
        else:
            self._goal = await self._infer_goal(text_to_improve)
            if not self._goal:
                self._goal = "Make this content clearer, more comprehensive, and more effective for its intended purpose"

        await self._emit_message(f"**🎯 Goal:** {self._goal}\n\n---\n\n")

        # Step 2: Generate dynamic metrics
        await self._emit_status("📊 Generating evaluation metrics...")
        metrics_ok = await self._generate_metrics(text_to_improve)
        if not metrics_ok:
            return f"⚠️ **Error:** Could not generate evaluation metrics.\n\nDetails: {self._last_error}"

        # Show the metrics we'll use
        metrics_display = self._format_metrics_display()
        await self._emit_append(
            f"**📊 Custom Evaluation Metrics:**\n{metrics_display}\n\n---\n\n"
        )

        # Step 3: Run MCTS
        await self._emit_status("🚀 Starting optimization search...")
        root = self._create_node(text_to_improve)

        try:
            best, stats = await self._run_mcts(root)
        except Exception as e:
            logger.error(f"MCTS failed: {e}")
            return f"⚠️ **Error:** {e}\n\nLast error: {self._last_error}"

        # Final output
        await self._emit_status(f"✅ Done! Best score: {stats['best_score']:.1f}/10")

        return self._format_final_output(best, root, stats)

    # ==========================================================================
    # GOAL INFERENCE
    # ==========================================================================

    async def _infer_goal(self, content: str) -> Optional[str]:
        """Use LLM to infer what the user wants to achieve."""
        preview = content[:1500] if len(content) > 1500 else content
        try:
            result = await self._llm_call(GOAL_INFERENCE_PROMPT, content=preview)
            if result and len(result.strip()) > 10:
                return result.strip()
        except Exception as e:
            self._last_error = str(e)
        return None

    # ==========================================================================
    # DYNAMIC METRICS
    # ==========================================================================

    async def _generate_metrics(self, content: str) -> bool:
        """Generate custom evaluation metrics based on the goal."""
        preview = content[:500] if len(content) > 500 else content

        try:
            result = await self._llm_call(
                METRICS_PROMPT, goal=self._goal, content_preview=preview
            )

            if not result:
                return False

            # Parse metrics
            lines = [
                l.strip() for l in result.strip().split("\n") if l.strip() and ":" in l
            ]

            if len(lines) < 3:
                # Fallback to default metrics
                self._metrics = [
                    "COMPLETENESS",
                    "CLARITY",
                    "DEPTH",
                    "ACCURACY",
                    "ENGAGEMENT",
                ]
                self._metrics_desc = {
                    "COMPLETENESS": "Covers all aspects of the goal",
                    "CLARITY": "Easy to understand and well-structured",
                    "DEPTH": "Sufficient detail and examples",
                    "ACCURACY": "Correct and well-reasoned",
                    "ENGAGEMENT": "Interesting and appropriate tone",
                }
                return True

            self._metrics = []
            self._metrics_desc = {}

            for line in lines[:5]:  # Max 5 metrics
                parts = line.split(":", 1)
                if len(parts) == 2:
                    name = parts[0].strip().upper().replace(" ", "_")
                    desc = parts[1].strip()
                    self._metrics.append(name)
                    self._metrics_desc[name] = desc

            # Ensure we have at least 3 metrics
            if len(self._metrics) < 3:
                return False

            return True

        except Exception as e:
            self._last_error = str(e)
            return False

    def _format_metrics_display(self) -> str:
        """Format metrics for display."""
        lines = []
        for i, metric in enumerate(self._metrics, 1):
            desc = self._metrics_desc.get(metric, "")
            lines.append(f"{i}. **{metric.replace('_', ' ').title()}**: {desc}")
        return "\n".join(lines)

    def _get_metrics_format(self) -> str:
        """Get the format string for evaluation response."""
        return "\n".join(f"{m}: [1-10]" for m in self._metrics)

    def _get_metrics_description(self) -> str:
        """Get full description of all metrics for prompts."""
        lines = []
        for m in self._metrics:
            lines.append(f"- {m}: {self._metrics_desc.get(m, '')}")
        return "\n".join(lines)

    # ==========================================================================
    # NODE OPERATIONS
    # ==========================================================================

    def _create_node(self, content: str, parent: dict = None) -> dict:
        self._node_counter += 1
        return {
            "id": f"n{self._node_counter}",
            "content": content,
            "parent": parent,
            "children": [],
            "visits": 0,
            "value": 0.0,
            "critique": "",
            "scores": None,  # Dict of metric -> score
            "iteration_created": 0,
        }

    def _avg_score(self, node: dict) -> float:
        return node["value"] / node["visits"] if node["visits"] > 0 else 0.0

    def _uct_value(self, node: dict) -> float:
        if node["visits"] == 0:
            return float("inf")
        parent = node["parent"]
        if parent is None or parent["visits"] == 0:
            return node["value"] / node["visits"]
        exploitation = node["value"] / node["visits"]
        exploration = self.valves.exploration_weight * math.sqrt(
            math.log(parent["visits"] + 1) / node["visits"]
        )
        
        # Depth bonus: encourage exploring deeper nodes
        depth = self._get_node_depth(node)
        depth_bonus = self.valves.depth_bonus * (depth / (depth + 2))  # Asymptotic bonus
        
        return exploitation + exploration + depth_bonus

    def _get_node_depth(self, node: dict) -> int:
        """Get depth of a specific node."""
        depth = 0
        current = node
        while current.get("parent"):
            depth += 1
            current = current["parent"]
        return depth

    def _fully_expanded(self, node: dict) -> bool:
        return len(node["children"]) >= self.valves.max_children

    def _add_child(self, parent: dict, child: dict):
        child["parent"] = parent
        parent["children"].append(child)

    def _count_nodes(self, node: dict) -> int:
        return 1 + sum(self._count_nodes(c) for c in node["children"])

    def _get_weakest_metric(self, scores: dict) -> str:
        """Get the metric with the lowest score."""
        if not scores:
            return self._metrics[0] if self._metrics else "UNKNOWN"
        metric_scores = {k: v for k, v in scores.items() if k in self._metrics}
        if not metric_scores:
            return self._metrics[0]
        return min(metric_scores, key=metric_scores.get)

    def _get_total_score(self, scores: dict) -> float:
        """Calculate weighted total from metric scores."""
        if not scores:
            return 1.0

        vals = [scores.get(m, 1.0) for m in self._metrics]
        if not vals:
            return 1.0

        # Simple average for now - all custom metrics weighted equally
        return sum(vals) / len(vals)

    # ==========================================================================
    # MCTS ALGORITHM
    # ==========================================================================

    async def _run_mcts(self, root: dict) -> tuple:
        best_score = 0.0
        best_node = root
        no_improvement = 0
        total_api_calls = 0
        iteration = 0
        self._best_score_history = []

        # Evaluate root
        await self._emit_status("📊 Evaluating initial content...")
        scores, calls = await self._evaluate_node(root, prev_best_score=None)
        total_api_calls += calls
        root["scores"] = scores

        initial_score = self._get_total_score(scores)
        self._backprop(root, initial_score)
        best_score = initial_score
        self._best_score_history.append({"iteration": 0, "score": initial_score, "node_id": root["id"]})

        # Show initial evaluation
        await self._emit_intermediate_result(root, 0, is_initial=True)

        if initial_score >= self.valves.early_stop_threshold:
            await self._emit_status("🎉 Content already excellent!")
            return best_node, self._build_stats(root, best_score, total_api_calls)

        # Main loop
        for i in range(self.valves.max_simulations):
            iteration = i + 1
            await self._emit_status(
                f"🔄 Iteration {iteration}/{self.valves.max_simulations} | Best: {best_score:.1f}/10"
            )

            # Select
            leaf = self._select(root)

            # Expand
            if leaf["visits"] > 0 and not self._fully_expanded(leaf):
                weak = self._get_weakest_metric(leaf.get("scores"))
                expanded, calls = await self._expand(leaf, weak, iteration)
                total_api_calls += calls

                if expanded:
                    leaf = expanded

                    # Evaluate the new node with comparative scoring
                    scores, eval_calls = await self._evaluate_node(leaf, prev_best_score=best_score)
                    total_api_calls += eval_calls
                    leaf["scores"] = scores

                    score = self._get_total_score(scores)
                    self._backprop(leaf, score)

                    # Show intermediate result with trajectory
                    if self.valves.show_intermediate:
                        await self._emit_intermediate_result(leaf, iteration)

                    # Track best
                    if score > best_score:
                        best_score = score
                        best_node = leaf
                        no_improvement = 0
                        self._best_score_history.append({"iteration": iteration, "score": score, "node_id": leaf["id"]})
                        await self._emit_status(f"⭐ New best: {score:.1f}/10!")
                    else:
                        no_improvement += 1
                else:
                    # Expansion failed, still backprop on leaf
                    scores, eval_calls = await self._evaluate_node(leaf, prev_best_score=best_score)
                    total_api_calls += eval_calls
                    leaf["scores"] = scores
                    score = self._get_total_score(scores)
                    self._backprop(leaf, score)
                    no_improvement += 1
            else:
                # Just simulate existing leaf
                if not leaf.get("scores"):
                    scores, eval_calls = await self._evaluate_node(leaf, prev_best_score=best_score)
                    total_api_calls += eval_calls
                    leaf["scores"] = scores

                score = self._get_total_score(leaf["scores"])
                self._backprop(leaf, score)
                no_improvement += 1

            # Update tree visualization with score trajectory
            await self._emit_tree_update(root, leaf["id"], iteration, best_score)

            # Check depth before early stopping
            current_depth = self._get_max_depth(root)
            
            # Early stopping (but respect min_depth)
            if best_score >= self.valves.early_stop_threshold and current_depth >= self.valves.min_depth:
                await self._emit_status(f"🎯 Reached target score at depth {current_depth}!")
                break

            if no_improvement >= self.valves.early_stop_patience and current_depth >= self.valves.min_depth:
                await self._emit_status(f"📈 Converged after {iteration} iterations (depth {current_depth})")
                break

        return best_node, self._build_stats(root, best_score, total_api_calls)
    
    def _get_max_depth(self, node: dict, current_depth: int = 0) -> int:
        """Get the maximum depth of the tree."""
        if not node["children"]:
            return current_depth
        return max(self._get_max_depth(c, current_depth + 1) for c in node["children"])
    
    def _get_node_depth(self, node: dict) -> int:
        """Get depth of a specific node."""
        depth = 0
        current = node
        while current.get("parent"):
            depth += 1
            current = current["parent"]
        return depth

    def _build_stats(self, root: dict, best_score: float, api_calls: int) -> dict:
        return {
            "nodes": self._count_nodes(root),
            "best_score": best_score,
            "total_api_calls": api_calls,
        }

    def _select(self, root: dict) -> dict:
        node = root
        while node["children"]:
            if not self._fully_expanded(node) and node["visits"] > 0:
                return node
            node = max(node["children"], key=self._uct_value)
        return node

    async def _expand(self, node: dict, weak_metric: str, iteration: int) -> tuple:
        """Expand node by creating variations. Returns (new_node, api_calls)."""
        total_calls = 0

        for attempt in range(2):
            tasks = [
                self._create_child(node, weak_metric, iteration)
                for _ in range(self.valves.num_thoughts)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            valid = []
            for r in results:
                if isinstance(r, tuple):
                    if r[0]:
                        valid.append(r[0])
                    total_calls += r[1]

            if valid:
                for child in valid:
                    self._add_child(node, child)
                return random.choice(valid), total_calls

        return None, total_calls

    async def _create_child(
        self, parent: dict, weak_metric: str, iteration: int
    ) -> tuple:
        """Create a single child node. Returns (node, api_calls)."""
        api_calls = 0

        try:
            # Get critique focused on weak metric
            weak_desc = self._metrics_desc.get(weak_metric, weak_metric)

            critique = await self._llm_call(
                THOUGHTS_PROMPT,
                goal=self._goal,
                metrics_description=self._get_metrics_description(),
                weak_area=f"{weak_metric}: {weak_desc}",
                answer=parent["content"],
            )
            api_calls += 1

            if not critique or len(critique.strip()) < 10:
                return None, api_calls

            # Generate improved content
            new_content = await self._llm_call(
                UPDATE_PROMPT,
                goal=self._goal,
                answer=parent["content"],
                improvements=critique.strip(),
            )
            api_calls += 1

            if not new_content or len(new_content.strip()) < 50:
                return None, api_calls

            new_content = new_content.strip()

            # Validation
            if len(new_content) < len(parent["content"]) * 0.7:
                return None, api_calls

            if self._similarity(parent["content"], new_content) > 0.95:
                return None, api_calls

            child = self._create_node(new_content, parent)
            child["critique"] = critique.strip()
            child["iteration_created"] = iteration

            return child, api_calls

        except Exception as e:
            self._last_error = str(e)
            return None, api_calls

    async def _evaluate_node(self, node: dict, prev_best_score: float = None) -> tuple:
        """Evaluate node with dynamic metrics. Returns (scores_dict, api_calls)."""
        try:
            # Build strictness-aware prompt
            strictness = self.valves.grading_strictness
            if strictness not in STRICTNESS_GUIDES:
                strictness = "strict"
            
            scoring_guide = STRICTNESS_GUIDES[strictness]
            persona = STRICTNESS_PERSONAS[strictness]
            
            # Comparative evaluation section
            comparative_section = ""
            if self.valves.comparative_eval and prev_best_score is not None:
                comparative_section = f"""
PREVIOUS BEST SCORE: {prev_best_score:.1f}/10
If you score this higher, you MUST see clear improvement. Don't inflate scores.
If similar quality, scores should be similar or lower."""
            
            response = await self._llm_call(
                EVAL_PROMPT,
                goal=self._goal,
                metrics_description=self._get_metrics_description(),
                metrics_format=self._get_metrics_format(),
                answer=node["content"],
                strictness=strictness,
                strictness_persona=persona,
                scoring_guide=scoring_guide,
                comparative_section=comparative_section,
            )

            if response:
                scores = self._parse_dynamic_scores(response)
                if scores:
                    return scores, 1

        except Exception as e:
            self._last_error = str(e)

        # Default scores
        return {m: 1.0 for m in self._metrics}, 1

    def _parse_dynamic_scores(self, response: str) -> Optional[dict]:
        """Parse scores for dynamic metrics."""
        scores = {}

        for metric in self._metrics:
            # Try exact match first
            pattern = rf"{metric}[:\s]*(\d+(?:\.\d+)?)"
            match = re.search(pattern, response, re.IGNORECASE)

            if not match:
                # Try with spaces instead of underscores
                alt_metric = metric.replace("_", r"[\s_]*")
                pattern = rf"{alt_metric}[:\s]*(\d+(?:\.\d+)?)"
                match = re.search(pattern, response, re.IGNORECASE)

            if match:
                val = float(match.group(1))
                scores[metric] = min(10.0, max(1.0, val))

        # Need at least half the metrics
        if len(scores) < len(self._metrics) / 2:
            # Try to extract any numbers as fallback
            nums = re.findall(r"\b(\d+(?:\.\d+)?)\b", response)
            nums = [float(n) for n in nums if 1 <= float(n) <= 10]

            if nums:
                avg = sum(nums) / len(nums)
                for m in self._metrics:
                    if m not in scores:
                        scores[m] = avg

        # Fill missing with average
        if scores:
            avg = sum(scores.values()) / len(scores)
            for m in self._metrics:
                if m not in scores:
                    scores[m] = avg

        return scores if scores else None

    def _backprop(self, node: dict, score: float):
        while node:
            node["visits"] += 1
            node["value"] += score
            node = node["parent"]

    def _similarity(self, a: str, b: str) -> float:
        a_words = set(a.lower().split())
        b_words = set(b.lower().split())
        if not a_words or not b_words:
            return 0.0
        return len(a_words & b_words) / len(a_words | b_words)

    # ==========================================================================
    # INTERMEDIATE OUTPUT
    # ==========================================================================

    async def _emit_intermediate_result(
        self, node: dict, iteration: int, is_initial: bool = False
    ):
        """Emit intermediate result for a node."""
        if not self.valves.show_intermediate:
            return

        scores = node.get("scores", {})
        total = self._get_total_score(scores)
        weak = self._get_weakest_metric(scores)

        # Format scores table
        score_lines = []
        for m in self._metrics:
            s = scores.get(m, 0)
            bar = "█" * int(s) + "░" * (10 - int(s))
            marker = " ⚠️" if m == weak else ""
            score_lines.append(
                f"| {m.replace('_', ' ').title()} | {bar} | {s:.1f}{marker} |"
            )

        scores_table = "\n".join(score_lines)

        # Content preview
        preview_len = self.valves.preview_length
        content_preview = node["content"][:preview_len]
        if len(node["content"]) > preview_len:
            content_preview += "..."

        # Build output
        depth = self._get_node_depth(node)
        if is_initial:
            header = f"### 📋 Initial Content (Score: {total:.1f}/10)"
        else:
            header = f"### 🔄 Iteration {iteration} → Node {node['id']} (Score: {total:.1f}/10 | Depth: {depth})"

        critique_section = ""
        if node.get("critique"):
            critique_section = f"\n**Applied Critique:** {node['critique'][:200]}{'...' if len(node['critique']) > 200 else ''}\n"

        # Score trajectory sparkline
        trajectory = self._format_score_trajectory()

        output = f"""
{header}

{trajectory}

| Metric | Score | Value |
|--------|-------|-------|
{scores_table}

**Total: {total:.1f}/10** | Weakest: {weak.replace('_', ' ').title()} | Strictness: {self.valves.grading_strictness}
{critique_section}
<details>
<summary>📄 Content Preview</summary>

{content_preview}

</details>

---

"""
        await self._emit_append(output)
    
    def _format_score_trajectory(self) -> str:
        """Format score history as ASCII sparkline."""
        if not self._best_score_history:
            return ""
        
        scores = [h["score"] for h in self._best_score_history]
        if len(scores) < 2:
            return f"📈 **Trajectory:** {scores[0]:.1f}"
        
        # ASCII sparkline
        blocks = " ▁▂▃▄▅▆▇█"
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s > min_s else 1
        
        sparkline = ""
        for s in scores:
            idx = int((s - min_s) / range_s * 8)
            sparkline += blocks[min(idx, 8)]
        
        # Node path
        path = " → ".join([f"{h['node_id']}({h['score']:.1f})" for h in self._best_score_history[-5:]])
        
        return f"📈 **Trajectory:** {scores[0]:.1f} {sparkline} {scores[-1]:.1f}\n   Path: {path}"

    async def _emit_tree_update(
        self, root: dict, current_id: str, iteration: int, best_score: float
    ):
        """Emit tree visualization update."""
        tree = self._generate_mermaid(root, current_id)
        max_depth = self._get_max_depth(root)

        output = f"""
<details open>
<summary>🌳 Search Tree (Iteration {iteration}) | Best: {best_score:.1f}/10 | Nodes: {self._count_nodes(root)} | Depth: {max_depth}</summary>

{tree}

</details>

"""
        # Use replace to update the tree section
        await self._emit_append(output)

    # ==========================================================================
    # FINAL OUTPUT
    # ==========================================================================

    def _format_final_output(self, best: dict, root: dict, stats: dict) -> str:
        """Format the final output."""
        scores = best.get("scores", {})
        total = self._get_total_score(scores)

        # Scores table
        score_rows = []
        for m in self._metrics:
            s = scores.get(m, 0)
            bar = "█" * int(s) + "░" * (10 - int(s))
            desc = self._metrics_desc.get(m, "")[:50]
            score_rows.append(
                f"| {m.replace('_', ' ').title()} | {bar} | **{s:.1f}** | {desc} |"
            )

        scores_table = "\n".join(score_rows)

        # Improvement path
        path = self._get_improvement_path(best)

        # Tree
        tree = self._generate_mermaid(root, best["id"])

        # Calculate improvement
        root_score = self._get_total_score(root.get("scores", {}))
        improvement = total - root_score
        improvement_str = (
            f"+{improvement:.1f}" if improvement > 0 else f"{improvement:.1f}"
        )

        return f"""
---

## ✨ Optimization Complete!

### 🎯 Goal
{self._goal}

### 📊 Final Scores

| Metric | Progress | Score | Description |
|--------|----------|-------|-------------|
{scores_table}

**Overall Score: {total:.1f}/10** ({improvement_str} improvement)

### 📈 Stats
- **Nodes explored:** {stats['nodes']}
- **API calls:** {stats['total_api_calls']}
- **Starting score:** {root_score:.1f}/10
- **Final score:** {total:.1f}/10

---

## 📝 Optimized Content

{best['content']}

---

<details>
<summary>🌳 Final Search Tree</summary>

{tree}

</details>

<details>
<summary>📈 Improvement Path</summary>

{path}

</details>

<details>
<summary>🎯 Metrics Used</summary>

{self._format_metrics_display()}

</details>
"""

    def _get_improvement_path(self, node: dict) -> str:
        """Get the path from root to this node."""
        path = []
        current = node
        while current:
            scores = current.get("scores", {})
            total = self._get_total_score(scores)
            critique = (current.get("critique") or "(root)")[:100]
            path.append(
                {
                    "id": current["id"],
                    "score": total,
                    "critique": critique,
                    "iteration": current.get("iteration_created", 0),
                }
            )
            current = current.get("parent")

        path.reverse()

        lines = []
        for i, p in enumerate(path):
            if i == 0:
                lines.append(f"⚑ **{p['id']}** (initial) - Score: {p['score']:.1f}/10")
            else:
                lines.append(
                    f"→ **{p['id']}** (iter {p['iteration']}) - Score: {p['score']:.1f}/10"
                )
                lines.append(f"   *Critique: {p['critique']}*")

        return "\n".join(lines)

    # ==========================================================================
    # VISUALIZATION
    # ==========================================================================

    def _escape(self, text: str) -> str:
        if not text:
            return ""
        for ch in [
            '"',
            "'",
            "(",
            ")",
            "\n",
            ";",
            "#",
            "<",
            ">",
            "{",
            "}",
            "[",
            "]",
            "|",
        ]:
            text = text.replace(ch, " ")
        return " ".join(text.split())[:30]

    def _generate_mermaid(self, root: dict, selected: str = None) -> str:
        lines = ["```mermaid", "graph TD"]
        self._mermaid_node(root, lines, selected)
        lines.append("```")
        return "\n".join(lines)

    def _mermaid_node(self, node: dict, lines: list, selected: str):
        nid = node["id"]
        score = round(self._avg_score(node), 1)
        visits = node["visits"]

        # Show weak metric in node
        weak = ""
        if node.get("scores"):
            weak = self._get_weakest_metric(node["scores"])[:4]

        lines.append(f'    {nid}["{nid}<br/>s:{score} v:{visits}<br/>{weak}"]')

        # Styling based on score
        if nid == selected:
            lines.append(f"    style {nid} stroke:#00ff00,stroke-width:4px")
        elif score >= 8:
            lines.append(f"    style {nid} fill:#90EE90,stroke:#228B22")
        elif score >= 6:
            lines.append(f"    style {nid} fill:#FFE4B5,stroke:#DDA000")
        elif score >= 4:
            lines.append(f"    style {nid} fill:#FFB6C1,stroke:#DC143C")
        else:
            lines.append(f"    style {nid} fill:#FF6B6B,stroke:#8B0000")

        for child in node["children"]:
            self._mermaid_node(child, lines, selected)
            # Edge label with score change
            parent_score = self._avg_score(node)
            child_score = self._avg_score(child)
            diff = child_score - parent_score
            diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
            lines.append(f"    {nid} -->|{diff_str}| {child['id']}")

    # ==========================================================================
    # LLM CALLS
    # ==========================================================================

    async def _llm_call(self, template: str, **kwargs) -> Optional[str]:
        for attempt in range(self.valves.max_retries):
            try:
                result = await self._llm_call_raw(template.format(**kwargs))
                if result:
                    return result
            except Exception as e:
                self._last_error = str(e)

            if attempt < self.valves.max_retries - 1:
                await asyncio.sleep((2**attempt) + random.uniform(0, 1))

        return None

    async def _llm_call_raw(self, prompt: str) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.valves.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openwebui.com/",
            "X-Title": "MCTS Optimizer",
        }

        payload = {
            "model": self.valves.thinking_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        url = f"{self.valves.base_url.rstrip('/')}/chat/completions"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.valves.timeout),
            ) as resp:
                text = await resp.text()

                if resp.status != 200:
                    self._last_error = f"API {resp.status}: {text[:200]}"
                    if resp.status in (429, 500, 502, 503):
                        raise aiohttp.ClientError(self._last_error)
                    return None

                data = json.loads(text)

                # Try multiple response formats
                for extractor in [
                    lambda d: d["choices"][0]["message"]["content"],
                    lambda d: d["choices"][0]["text"],
                    lambda d: d["output"],
                    lambda d: d["content"],
                    lambda d: d["response"],
                ]:
                    try:
                        content = extractor(data)
                        if content:
                            return content.strip()
                    except (KeyError, IndexError, TypeError):
                        continue

                self._last_error = f"Unknown response: {str(data)[:200]}"
                return None

    async def _test_api(self) -> bool:
        try:
            result = await self._llm_call_raw("Reply with only: OK")
            return bool(result)
        except Exception as e:
            self._last_error = str(e)
            return False

    # ==========================================================================
    # EVENT EMITTERS
    # ==========================================================================

    async def _emit_status(self, msg: str, done: bool = False):
        if self._emitter:
            await self._emitter(
                {"type": "status", "data": {"description": msg, "done": done}}
            )

    async def _emit_message(self, content: str):
        """Emit initial message content."""
        if self._emitter:
            await self._emitter({"type": "message", "data": {"content": content}})

    async def _emit_append(self, content: str):
        """Append to message content."""
        if self._emitter:
            await self._emitter({"type": "message", "data": {"content": content}})

    async def _emit_replace(self, content: str):
        """Replace message content."""
        if self._emitter:
            await self._emitter({"type": "replace", "data": {"content": content}})
