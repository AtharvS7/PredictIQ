"""
PredictIQ NLP Feature Extractor Service
=========================================
Extracts project parameters from parsed document text.
Uses regex patterns + keyword matching to identify:
- Project type, tech stack, team size, duration
- Complexity, methodology, feature count
- Project name

Returns dict[str, {value, confidence}] for each field.
All values feed into ml_service._build_feature_vector().
"""

import re
import structlog
from typing import Optional

logger = structlog.get_logger()


# ══════════════════════════════════════════════════════════════════════
# Keyword libraries
# ══════════════════════════════════════════════════════════════════════

TECH_KEYWORDS: dict[str, list[str]] = {
    "frontend": [
        "react", "react.js", "reactjs", "react js",
        "vue", "vue.js", "vuejs", "vue js",
        "angular", "angular.js", "angularjs", "angular js",
        "svelte", "nextjs", "next.js", "next js",
        "nuxt", "nuxt.js", "nuxtjs",
        "typescript", "javascript", "html", "css",
        "tailwind", "tailwindcss",
        "bootstrap", "flutter", "swiftui",
        "webpack", "vite",
        "electron", "electron.js", "electronjs",
        "solid.js", "solidjs", "gatsby", "gatsby.js", "gatsbyjs",
        "remix", "remix.js", "remixjs", "htmx", "astro",
    ],
    "backend": [
        "fastapi", "fast api", "django", "flask",
        "express", "express.js", "expressjs",
        "nodejs", "node.js", "node js", "node",
        "spring", "spring boot",
        "laravel", "rails", "ruby on rails",
        "dotnet", ".net",
        "go", "golang", "rust",
        "graphql", "rest api",
        "nestjs", "nest.js",
        "deno", "bun", "hono",
        "grpc", "django rest framework", "drf",
        "python", "java", "c#", "c++", "php", "ruby",
        "scala", "elixir",
    ],
    "database": [
        "postgresql", "postgres", "mysql", "mongodb",
        "supabase", "firebase",
        "redis", "sqlite", "dynamodb",
        "elasticsearch", "cassandra", "neo4j",
        "planetscale", "neon", "turso",
        "drizzle", "prisma", "sqlalchemy",
        "qdrant", "weaviate", "pinecone", "chroma",
        "clickhouse", "snowflake", "bigquery",
    ],
    "ml": [
        "machine learning", "deep learning",
        "tensorflow", "pytorch", "scikit-learn", "xgboost",
        "nlp", "llm", "gpt", "bert",
        "neural network", "ai model", "computer vision", "opencv",
        "langchain", "llamaindex", "llama index",
        "openai", "anthropic", "gemini", "claude",
        "hugging face", "huggingface", "transformers",
        "ollama", "mistral", "llama 3",
        "stable diffusion", "whisper", "tesseract",
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "swift", "kotlin",
        "xamarin", "objective-c",
    ],
    "devops": [
        "docker", "kubernetes", "k8s",
        "aws", "azure", "gcp", "google cloud",
        "ci/cd", "github actions", "gitlab ci",
        "terraform", "ansible", "nginx",
        "vercel", "netlify", "fly.io", "render", "railway",
        "heroku", "digitalocean",
        "cloudflare workers", "cloudflare pages", "cloudflare",
        "pulumi", "puppet", "chef",
        "prometheus", "grafana", "datadog", "sentry",
    ],
}

# Flatten for quick lookup
ALL_TECH_KEYWORDS: set[str] = set()
for _cat_keywords in TECH_KEYWORDS.values():
    ALL_TECH_KEYWORDS.update(_cat_keywords)

# Display name mapping for proper capitalization
TECH_DISPLAY_NAMES: dict[str, str] = {
    "react": "React", "react.js": "React", "reactjs": "React", "react js": "React",
    "vue": "Vue", "vue.js": "Vue", "vuejs": "Vue", "vue js": "Vue",
    "angular": "Angular", "angular.js": "Angular", "angularjs": "Angular",
    "angular js": "Angular",
    "svelte": "Svelte", "next.js": "Next.js", "nextjs": "Next.js",
    "next js": "Next.js",
    "nuxt": "Nuxt", "nuxt.js": "Nuxt", "nuxtjs": "Nuxt",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
    "node js": "Node.js",
    "express": "Express", "express.js": "Express", "expressjs": "Express",
    "typescript": "TypeScript", "javascript": "JavaScript",
    "fastapi": "FastAPI", "fast api": "FastAPI",
    "django": "Django", "flask": "Flask", "laravel": "Laravel",
    "spring": "Spring", "spring boot": "Spring Boot",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL", "mongodb": "MongoDB",
    "supabase": "Supabase", "firebase": "Firebase",
    "redis": "Redis", "sqlite": "SQLite",
    "dynamodb": "DynamoDB", "elasticsearch": "Elasticsearch",
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn", "xgboost": "XGBoost",
    "graphql": "GraphQL", "rest api": "REST API",
    "golang": "Go", "go": "Go", "rust": "Rust",
    "python": "Python", "java": "Java", "c#": "C#", "c++": "C++",
    "php": "PHP", "ruby": "Ruby", "scala": "Scala", "elixir": "Elixir",
    "nestjs": "NestJS", "nest.js": "NestJS",
    "prisma": "Prisma", "drizzle": "Drizzle", "sqlalchemy": "SQLAlchemy",
    "langchain": "LangChain", "openai": "OpenAI",
    "anthropic": "Anthropic", "gemini": "Gemini",
    "vercel": "Vercel", "netlify": "Netlify", "heroku": "Heroku",
    "cloudflare": "Cloudflare", "aws": "AWS", "azure": "Azure", "gcp": "GCP",
    "react native": "React Native", "flutter": "Flutter",
    "swift": "Swift", "kotlin": "Kotlin",
    "html": "HTML", "css": "CSS",
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap", "webpack": "Webpack", "vite": "Vite",
    "remix": "Remix", "remix.js": "Remix", "remixjs": "Remix",
    "astro": "Astro", "htmx": "HTMX",
    "solid.js": "SolidJS", "solidjs": "SolidJS",
    "gatsby": "Gatsby", "gatsby.js": "Gatsby", "gatsbyjs": "Gatsby",
    "electron": "Electron", "electron.js": "Electron", "electronjs": "Electron",
    "grpc": "gRPC", "deno": "Deno", "bun": "Bun", "hono": "Hono",
    "sentry": "Sentry", "datadog": "Datadog",
    "prometheus": "Prometheus", "grafana": "Grafana",
    "nginx": "Nginx", "terraform": "Terraform",
}

PROJECT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Web App": [
        "web app", "website", "web application", "web platform", "saas",
        "web portal", "dashboard", "admin panel", "cms",
    ],
    "Mobile App": [
        "mobile app", "ios app", "android app", "mobile application",
        "react native", "flutter app", "cross-platform",
    ],
    "API/Backend": [
        "api", "backend", "microservice", "rest api", "graphql api",
        "web service", "api gateway",
    ],
    "ML/AI System": [
        "machine learning", "ai system", "deep learning", "neural network",
        "nlp", "computer vision", "model training", "recommendation engine",
    ],
    "Data Platform": [
        "data pipeline", "etl", "data warehouse", "analytics",
        "data lake", "big data", "data platform",
    ],
    "Enterprise Software": [
        "enterprise", "erp", "crm", "hrm", "supply chain",
        "business process", "b2b", "legacy modernization",
    ],
}

COMPLEXITY_SIGNALS: dict[str, list[str]] = {
    "Very High": [
        "enterprise", "complex", "advanced", "sophisticated",
        "large-scale", "high-performance", "distributed", "microservices",
        "real-time", "mission-critical", "multi-tenant", "encryption",
        "compliance", "hipaa", "gdpr", "pci",
    ],
    "High": [
        "integration", "multiple", "custom", "authentication",
        "payment", "analytics", "reporting", "dashboard", "api",
        "scalable", "high availability", "load balancing",
    ],
    "Medium": [
        "standard", "typical", "moderate", "normal",
    ],
    "Low": [
        "simple", "minimal", "small", "basic", "static",
        "prototype", "mvp", "poc", "proof of concept", "landing page",
    ],
}

METHODOLOGY_KEYWORDS: dict[str, list[str]] = {
    "Agile": [
        "agile", "scrum", "sprint", "kanban", "story points",
        "backlog", "iteration", "standup", "retrospective",
        "user story", "product owner",
    ],
    "Waterfall": [
        "waterfall", "phase", "milestone", "sequential",
        "requirements document", "design phase", "stage gate",
    ],
    "Hybrid": [
        "hybrid", "mixed", "flexible",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Duration patterns
# ══════════════════════════════════════════════════════════════════════

DURATION_PATTERNS: list[tuple[str, Optional[callable]]] = [
    (r"(\d+)\s*[-–]?\s*months?", lambda m: float(m.group(1))),
    (r"(\d+)\s*[-–]?\s*weeks?", lambda m: float(m.group(1)) / 4.33),
    (r"(\d+)\s*[-–]?\s*days?", lambda m: float(m.group(1)) / 30),
    (r"(\d+)\s*[-–]?\s*sprints?", lambda m: float(m.group(1)) * 2 / 4.33),
]

DURATION_WORDS: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twelve": 12, "eighteen": 18, "twenty-four": 24,
}

# Team size patterns
TEAM_PATTERNS: list[str] = [
    r"team\s+(?:of\s+)?(\d+)",
    r"(\d+)\s+developers?",
    r"(\d+)\s+engineers?",
    r"(\d+)\s+person\s+team",
    r"(\d+)\s+members?",
    r"headcount\s+(?:of\s+)?(\d+)",
    r"(\d+)\s+(?:people|staff|resources)",
    r"team\s*(?:size)?\s*:?\s*(\d+)",
]

# Feature/story count patterns
FEATURE_PATTERNS: list[str] = [
    r"(\d+)\s+features?",
    r"(\d+)\s+user\s+stories?",
    r"(\d+)\s+requirements?",
    r"(\d+)\s+modules?",
    r"(\d+)\s+epics?",
    r"(\d+)\s+use\s+cases?",
    r"(\d+)\s+screens?",
    r"(\d+)\s+pages?",
    r"(\d+)\s+functionalities?",
    r"(\d+)\s+endpoints?",
]


class NLPExtractor:
    """Extracts project parameters from document text."""

    def extract(self, text: str) -> dict:
        """
        Analyze document text and extract project parameters.

        Args:
            text: Raw document text from the parser.

        Returns:
            Dict with keys like 'project_type', 'tech_stack', etc.
            Each value is {value: ..., confidence: float}.
        """
        if not text or len(text.strip()) < 10:
            logger.warning("nlp_extract_empty_text")
            return self._default_extraction()

        text_lower = text.lower()

        tech_stack = self._extract_tech_stack(text_lower)
        feature_count = self._count_features(text)
        complexity = self._estimate_complexity(
            text_lower,
            tech_stack["value"],
            feature_count["value"],
        )
        project_type = self._extract_project_type(
            text_lower, tech_stack["value"]
        )

        extracted = {
            "project_type": project_type,
            "tech_stack": tech_stack,
            "team_size": self._extract_team_size(text_lower),
            "duration_months": self._extract_duration(text_lower),
            "complexity": complexity,
            "methodology": self._extract_methodology(text_lower),
            "feature_count": feature_count,
            "project_name": self._extract_project_name(text),
        }

        logger.info(
            "nlp_extraction_complete",
            project_type=extracted["project_type"]["value"],
            complexity=extracted["complexity"]["value"],
            features=extracted["feature_count"]["value"],
            tech_count=len(extracted["tech_stack"]["value"]),
        )
        return extracted

    def _default_extraction(self) -> dict:
        """Return safe defaults when text is empty/too short."""
        return {
            "project_type": {"value": "Web App", "confidence": 0.2},
            "tech_stack": {"value": [], "confidence": 0.1},
            "team_size": {"value": 5, "confidence": 0.2},
            "duration_months": {"value": 6.0, "confidence": 0.2},
            "complexity": {"value": "Medium", "confidence": 0.2},
            "methodology": {"value": "Agile", "confidence": 0.2},
            "feature_count": {"value": 10, "confidence": 0.2},
            "project_name": {"value": "Untitled Project", "confidence": 0.1},
        }

    def _extract_project_type(
        self, text: str, tech_stack: list[str]
    ) -> dict:
        """Identify project type from text keywords."""
        scores: dict[str, int] = {}
        for ptype, keywords in PROJECT_TYPE_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                scores[ptype] = count

        # Boost based on tech stack
        tech_lower = [t.lower() for t in tech_stack]
        ml_techs = {"machine learning", "pytorch", "tensorflow", "xgboost", "scikit-learn"}
        mobile_techs = {"react native", "flutter", "swift", "kotlin", "android", "ios"}

        if ml_techs & set(tech_lower):
            scores["ML/AI System"] = scores.get("ML/AI System", 0) + 2
        if mobile_techs & set(tech_lower):
            scores["Mobile App"] = scores.get("Mobile App", 0) + 2

        if scores:
            best = max(scores, key=scores.get)  # type: ignore[arg-type]
            confidence = min(0.9, scores[best] * 0.2)
            return {"value": best, "confidence": confidence}

        return {"value": "Web App", "confidence": 0.3}

    def _extract_tech_stack(self, text: str) -> dict:
        """Find technology mentions in the text."""
        found: list[str] = []

        # Sort keywords by length descending so multi-word matches go first
        sorted_keywords = sorted(ALL_TECH_KEYWORDS, key=len, reverse=True)

        for tech in sorted_keywords:
            # Use word boundary matching for ALL keywords to avoid false positives
            pattern = r"\b" + re.escape(tech) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                found.append(tech)

        # Deduplicate using display names to collapse variants
        seen_display: set[str] = set()
        unique: list[str] = []
        for t in found:
            t_lower = t.lower()
            # Use canonical display name if available
            display = TECH_DISPLAY_NAMES.get(t_lower)
            if display is None:
                display = t.title() if len(t) > 3 else t.upper()

            if display not in seen_display:
                seen_display.add(display)
                unique.append(display)

        confidence = min(0.95, len(unique) * 0.08) if unique else 0.2
        return {"value": unique[:15], "confidence": confidence}

    def _extract_team_size(self, text: str) -> dict:
        """Extract team size from text."""
        for pattern in TEAM_PATTERNS:
            m = re.search(pattern, text)
            if m:
                size = int(m.group(1))
                if 1 <= size <= 100:
                    return {"value": size, "confidence": 0.75}

        # Word-based: "five developers"
        for word, num in DURATION_WORDS.items():
            if re.search(
                rf"\b{word}\s+(?:person|developer|engineer|member)", text
            ):
                return {"value": num, "confidence": 0.6}

        return {"value": 5, "confidence": 0.3}

    def _extract_duration(self, text: str) -> dict:
        """Extract project duration in months."""
        for pattern, converter in DURATION_PATTERNS:
            m = re.search(pattern, text)
            if m and converter:
                months = converter(m)
                if 0.5 <= months <= 60:
                    return {"value": round(months, 1), "confidence": 0.75}

        # Word-based: "six months"
        for word, num in DURATION_WORDS.items():
            if re.search(rf"\b{word}\s+months?", text):
                return {"value": float(num), "confidence": 0.65}

        return {"value": 6.0, "confidence": 0.3}

    def _estimate_complexity(
        self,
        text: str,
        tech_stack: list[str],
        feature_count: int,
    ) -> dict:
        """Estimate project complexity from indicators."""
        scores: dict[str, int] = {"Low": 0, "Medium": 0, "High": 0, "Very High": 0}

        for level, signals in COMPLEXITY_SIGNALS.items():
            for signal in signals:
                if signal in text:
                    scores[level] += 1

        # Tech stack complexity boost
        tech_lower = [t.lower() for t in tech_stack]
        ml_techs = {"machine learning", "pytorch", "tensorflow", "xgboost"}
        if set(tech_lower) & ml_techs:
            scores["Very High"] += 2

        if len(tech_stack) > 8:
            scores["High"] += 1
        if feature_count > 20:
            scores["High"] += 1
        if feature_count > 40:
            scores["Very High"] += 1

        # Word count as complexity signal
        word_count = len(text.split())
        if word_count > 5000:
            scores["High"] += 1
        if word_count > 10000:
            scores["Very High"] += 1

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        total = sum(scores.values())
        confidence = min(0.8, 0.3 + total * 0.05) if total > 0 else 0.3
        return {
            "value": best if total > 0 else "Medium",
            "confidence": confidence,
        }

    def _extract_methodology(self, text: str) -> dict:
        """Identify development methodology."""
        method_scores: dict[str, int] = {}
        for method, keywords in METHODOLOGY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                method_scores[method] = count

        if method_scores:
            best = max(method_scores, key=method_scores.get)  # type: ignore[arg-type]
            confidence = min(0.85, method_scores[best] * 0.15)
            return {"value": best, "confidence": confidence}

        return {"value": "Agile", "confidence": 0.3}

    def _count_features(self, text: str) -> dict:
        """Estimate the number of features/requirements."""
        text_lower = text.lower()

        # Check explicit count mentions
        explicit_counts: list[int] = []
        for pattern in FEATURE_PATTERNS:
            for m in re.finditer(pattern, text_lower):
                n = int(m.group(1))
                if 1 <= n <= 200:
                    explicit_counts.append(n)

        if explicit_counts:
            count = max(explicit_counts)
            return {"value": count, "confidence": 0.8}

        # Count bullet-point style requirements
        bullet_count = len(re.findall(r"(?:^|\n)\s*[-•*]\s+\w", text))
        numbered_count = len(re.findall(r"(?:^|\n)\s*\d+\.\s+\w", text))
        feature_mentions = len(
            re.findall(
                r"(?:feature|requirement|user story|functionality|capability)",
                text,
                re.IGNORECASE,
            )
        )

        # Use best available signal
        structural_count = bullet_count + numbered_count
        if structural_count > 3:
            return {"value": min(structural_count, 50), "confidence": 0.55}
        if feature_mentions > 0:
            return {"value": max(feature_mentions, 5), "confidence": 0.4}

        return {"value": 10, "confidence": 0.3}

    def _extract_project_name(self, text: str) -> dict:
        """
        Extract the project name from document content only.

        Never falls back to the uploaded filename. If no pattern matches,
        returns an empty string so the user must fill it in manually.
        """
        patterns = [
            # Explicit labels: "Project Name: ...", "Title: ...", etc.
            r"(?:project\s+name|system\s+name|application\s+name|product\s+name|title)\s*[:\-–]\s*[\"']?([\w][\w\s\-\.]{2,75})",
            # Markdown heading with system/app suffix
            r"(?:^|\n)#{1,3}\s+([A-Z][\w\s]{3,40}?)\s*(?:system|application|platform|portal|app|project)",
            # "Proposal for ...", "Estimation for ...", "Quote for ..."
            r"(?:proposal\s+for|estimation\s+for|quote\s+for)\s+([\w][\w\s]{2,50}?)(?:\.|\n|$)",
            # Document type header: "XYZ SRS/PRD/BRD"
            r"(?:^|\n)([A-Z][\w\s]{3,40}?)\s*(?:SRS|PRD|BRD|specification|requirements\s+document)",
            # Simple "Project Name: ..." with quotes
            r"project\s*(?:name|title)?\s*:\s*[\"']?([A-Z][A-Za-z0-9\s\-]{2,30})",
            # First markdown heading
            r"^#\s+(.{3,50})$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = match.group(1).strip().rstrip(".,;:")
                # Validate: skip very short or obviously non-name strings
                if 2 < len(name) <= 80 and not name.lower().startswith(("http", "www", "file")):
                    return {"value": name[:80], "confidence": 0.65}

        # No pattern matched — return empty string so user must fill it in.
        # NEVER use the first line or filename as a fallback.
        return {"value": "", "confidence": 0.0}


nlp_extractor = NLPExtractor()
