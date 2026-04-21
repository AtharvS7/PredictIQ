"""
PredictIQ NLP Feature Extractor Service v2.4
=============================================
Industrial-grade, multi-strategy extraction engine for SRS, PRD,
RFP, and proposal documents.

Architecture: 4-strategy cascade
    1. Structural analysis — parse tables, headers, lists
    2. Section-aware extraction — identify relevant sections by header
    3. Global pattern matching — regex across full text
    4. Cross-validation — reconcile conflicts by confidence

Returns dict[str, {value, confidence}] for each field.
All values feed into ml_service._build_feature_vector().
"""

import re
import structlog
from dataclasses import dataclass, field
from typing import Any, Optional

logger = structlog.get_logger()


# ══════════════════════════════════════════════════════════════════════
# Data Classes
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ExtractionResult:
    """Result from a single extraction method."""
    value: Any
    confidence: float  # 0.0-1.0
    evidence: list[str] = field(default_factory=list)
    strategy: str = "default"

    def to_dict(self) -> dict:
        return {"value": self.value, "confidence": self.confidence}


@dataclass
class DocumentStructure:
    """Pre-processed document representation."""
    full_text: str
    text_lower: str
    raw_lines: list[str]
    headers: list[dict]        # {level: int, text: str, line_num: int}
    tables: list[str]          # Parsed table rows as flat strings
    list_items: list[str]      # All bullet/numbered list items
    sections: dict[str, str]   # section_header_lower -> section_body_text
    word_count: int


# ══════════════════════════════════════════════════════════════════════
# Keyword Dictionaries (300+ keywords)
# ══════════════════════════════════════════════════════════════════════

TECH_KEYWORDS: dict[str, list[str]] = {
    "frontend": [
        "react", "react.js", "reactjs", "react js",
        "vue", "vue.js", "vuejs", "vue js",
        "angular", "angular.js", "angularjs", "angular js",
        "svelte", "sveltekit",
        "nextjs", "next.js", "next js",
        "nuxt", "nuxt.js", "nuxtjs",
        "typescript", "javascript", "es6",
        "html", "html5", "css", "css3", "sass", "scss", "less",
        "tailwind", "tailwindcss", "bootstrap", "material-ui", "shadcn", "ant design",
        "webpack", "vite", "parcel", "rollup", "esbuild",
        "redux", "zustand", "mobx", "recoil", "jotai", "pinia",
        "react native", "expo", "ionic", "cordova", "capacitor",
        "flutter", "dart",
        "electron", "electron.js", "electronjs", "tauri",
        "solid.js", "solidjs", "gatsby", "gatsby.js", "gatsbyjs",
        "remix", "remix.js", "remixjs", "htmx", "astro",
        "alpine.js", "lit", "web components",
        "three.js", "d3.js", "chart.js", "echarts", "recharts",
        "framer motion", "gsap",
        "swiftui",
    ],
    "backend": [
        "fastapi", "fast api",
        "django", "django rest framework", "drf",
        "flask", "flask-restful",
        "express", "express.js", "expressjs", "koa", "hono", "fastify",
        "nestjs", "nest.js",
        "spring boot", "spring", "spring framework",
        "laravel", "symfony", "codeigniter",
        "rails", "ruby on rails",
        "asp.net", ".net core", ".net", "dotnet",
        "gin", "echo", "fiber",
        "actix", "axum",
        "nodejs", "node.js", "node js", "node",
        "deno", "bun",
        "python", "java", "golang", "go", "rust", "kotlin", "swift",
        "php", "ruby", "scala", "elixir", "c#", "c++",
        "graphql", "rest api", "grpc", "websockets", "socket.io",
        "celery", "dramatiq",
        "nginx", "apache", "caddy",
        "gunicorn", "uvicorn",
    ],
    "database": [
        "postgresql", "postgres", "mysql", "mariadb",
        "mongodb", "mongoose",
        "sqlite",
        "supabase", "firebase", "firestore",
        "redis", "memcached",
        "dynamodb", "cosmosdb",
        "elasticsearch", "opensearch",
        "cassandra", "scylladb",
        "neo4j", "arangodb",
        "snowflake", "bigquery", "redshift", "databricks",
        "clickhouse",
        "qdrant", "pinecone", "weaviate", "chroma", "milvus", "pgvector",
        "prisma", "drizzle", "sqlalchemy", "sequelize", "typeorm", "hibernate",
        "planetscale", "neon", "turso",
    ],
    "ml_ai": [
        "machine learning", "deep learning",
        "tensorflow", "pytorch", "keras", "jax",
        "scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
        "hugging face", "huggingface", "transformers", "bert", "gpt", "llm",
        "langchain", "llamaindex", "llama index",
        "openai", "anthropic", "gemini", "mistral", "ollama", "groq",
        "stable diffusion",
        "whisper", "tesseract", "spacy", "nltk",
        "mlflow", "wandb",
        "opencv", "computer vision",
        "neural network", "ai model",
        "nlp", "natural language processing",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "swift", "kotlin",
        "xamarin", "objective-c",
        "app store", "play store",
    ],
    "devops_cloud": [
        "docker", "kubernetes", "k8s", "helm",
        "aws", "amazon web services", "ec2", "s3", "lambda", "rds",
        "azure", "microsoft azure",
        "gcp", "google cloud", "cloud run",
        "vercel", "netlify", "render", "railway", "fly.io", "heroku",
        "cloudflare", "cloudflare workers", "cloudflare pages",
        "terraform", "pulumi", "ansible",
        "github actions", "gitlab ci", "jenkins", "circle ci",
        "ci/cd", "continuous integration",
        "prometheus", "grafana", "datadog", "sentry", "new relic",
        "kafka", "rabbitmq", "sqs",
        "digitalocean",
    ],
    "security_auth": [
        "oauth2", "oauth", "oidc",
        "jwt", "json web token",
        "ssl", "tls",
        "pci-dss", "pci dss", "hipaa", "gdpr", "soc2", "iso27001",
        "two-factor authentication", "2fa", "mfa",
        "ldap", "active directory", "saml", "sso",
        "auth0", "cognito", "keycloak",
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
    "svelte": "Svelte", "sveltekit": "SvelteKit",
    "next.js": "Next.js", "nextjs": "Next.js", "next js": "Next.js",
    "nuxt": "Nuxt", "nuxt.js": "Nuxt", "nuxtjs": "Nuxt",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js", "node js": "Node.js",
    "express": "Express", "express.js": "Express", "expressjs": "Express",
    "typescript": "TypeScript", "javascript": "JavaScript",
    "html": "HTML", "html5": "HTML5", "css": "CSS", "css3": "CSS3",
    "sass": "Sass", "scss": "SCSS", "less": "Less",
    "fastapi": "FastAPI", "fast api": "FastAPI",
    "django": "Django", "django rest framework": "Django REST Framework", "drf": "DRF",
    "flask": "Flask", "flask-restful": "Flask-RESTful",
    "laravel": "Laravel", "symfony": "Symfony",
    "spring": "Spring", "spring boot": "Spring Boot", "spring framework": "Spring",
    "rails": "Rails", "ruby on rails": "Ruby on Rails",
    "asp.net": "ASP.NET", ".net core": ".NET Core", ".net": ".NET", "dotnet": ".NET",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL", "mariadb": "MariaDB",
    "mongodb": "MongoDB", "mongoose": "Mongoose",
    "sqlite": "SQLite",
    "supabase": "Supabase", "firebase": "Firebase", "firestore": "Firestore",
    "redis": "Redis", "memcached": "Memcached",
    "dynamodb": "DynamoDB", "cosmosdb": "CosmosDB",
    "elasticsearch": "Elasticsearch", "opensearch": "OpenSearch",
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "keras": "Keras",
    "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
    "xgboost": "XGBoost", "lightgbm": "LightGBM",
    "graphql": "GraphQL", "rest api": "REST API", "grpc": "gRPC",
    "golang": "Go", "go": "Go", "rust": "Rust",
    "python": "Python", "java": "Java", "c#": "C#", "c++": "C++",
    "php": "PHP", "ruby": "Ruby", "scala": "Scala", "elixir": "Elixir",
    "kotlin": "Kotlin", "swift": "Swift", "dart": "Dart",
    "nestjs": "NestJS", "nest.js": "NestJS",
    "prisma": "Prisma", "drizzle": "Drizzle", "sqlalchemy": "SQLAlchemy",
    "sequelize": "Sequelize", "typeorm": "TypeORM", "hibernate": "Hibernate",
    "langchain": "LangChain", "openai": "OpenAI",
    "anthropic": "Anthropic", "gemini": "Gemini", "mistral": "Mistral",
    "vercel": "Vercel", "netlify": "Netlify", "heroku": "Heroku",
    "cloudflare": "Cloudflare", "aws": "AWS", "azure": "Azure", "gcp": "GCP",
    "google cloud": "Google Cloud",
    "react native": "React Native", "flutter": "Flutter",
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap", "material-ui": "Material UI",
    "webpack": "Webpack", "vite": "Vite", "parcel": "Parcel",
    "redux": "Redux", "zustand": "Zustand", "mobx": "MobX",
    "remix": "Remix", "remix.js": "Remix", "remixjs": "Remix",
    "astro": "Astro", "htmx": "HTMX",
    "solid.js": "SolidJS", "solidjs": "SolidJS",
    "gatsby": "Gatsby", "gatsby.js": "Gatsby", "gatsbyjs": "Gatsby",
    "electron": "Electron", "electron.js": "Electron", "electronjs": "Electron",
    "tauri": "Tauri",
    "deno": "Deno", "bun": "Bun", "hono": "Hono",
    "sentry": "Sentry", "datadog": "Datadog", "new relic": "New Relic",
    "prometheus": "Prometheus", "grafana": "Grafana",
    "nginx": "Nginx", "terraform": "Terraform", "ansible": "Ansible",
    "kafka": "Kafka", "rabbitmq": "RabbitMQ",
    "github actions": "GitHub Actions", "gitlab ci": "GitLab CI",
    "jenkins": "Jenkins",
    "snowflake": "Snowflake", "bigquery": "BigQuery", "redshift": "Redshift",
    "clickhouse": "ClickHouse",
    "neo4j": "Neo4j",
    "cassandra": "Cassandra",
    "qdrant": "Qdrant", "pinecone": "Pinecone", "weaviate": "Weaviate",
    "chroma": "Chroma", "pgvector": "pgvector",
    "oauth2": "OAuth2", "jwt": "JWT",
    "auth0": "Auth0", "cognito": "Cognito", "keycloak": "Keycloak",
    "websockets": "WebSockets", "socket.io": "Socket.IO",
    "celery": "Celery",
    "digitalocean": "DigitalOcean",
    "fly.io": "Fly.io", "render": "Render", "railway": "Railway",
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "neural network": "Neural Network", "ai model": "AI Model",
    "computer vision": "Computer Vision",
    "nlp": "NLP", "natural language processing": "NLP",
    "opencv": "OpenCV",
    "hugging face": "HuggingFace", "huggingface": "HuggingFace",
    "transformers": "Transformers",
    "llm": "LLM", "gpt": "GPT", "bert": "BERT",
    "ollama": "Ollama", "groq": "Groq",
    "stable diffusion": "Stable Diffusion",
    "whisper": "Whisper", "tesseract": "Tesseract",
    "spacy": "spaCy", "nltk": "NLTK",
    "pandas": "Pandas", "numpy": "NumPy", "scipy": "SciPy",
    "matplotlib": "Matplotlib", "seaborn": "Seaborn", "plotly": "Plotly",
    "mlflow": "MLflow", "wandb": "W&B",
    "ci/cd": "CI/CD", "continuous integration": "CI/CD",
    "pci-dss": "PCI-DSS", "pci dss": "PCI-DSS",
    "hipaa": "HIPAA", "gdpr": "GDPR", "soc2": "SOC2",
    "sso": "SSO", "saml": "SAML", "ldap": "LDAP",
    "2fa": "2FA", "mfa": "MFA",
    "three.js": "Three.js", "d3.js": "D3.js",
    "chart.js": "Chart.js", "echarts": "ECharts", "recharts": "Recharts",
    "framer motion": "Framer Motion", "gsap": "GSAP",
    "alpine.js": "Alpine.js",
    "expo": "Expo", "ionic": "Ionic",
    "helm": "Helm",
    "ec2": "EC2", "s3": "S3", "lambda": "Lambda", "rds": "RDS",
    "pulumi": "Pulumi",
}

PROJECT_TYPE_SIGNALS: dict[str, dict[str, list[str]]] = {
    "Web App": {
        "high": ["web application", "browser-based", "responsive design", "spa",
                 "progressive web app", "pwa", "web app", "saas"],
        "medium": ["frontend", "web interface", "web portal", "web platform",
                   "website", "dashboard", "admin panel", "cms"],
    },
    "Mobile App": {
        "high": ["mobile application", "android app", "ios app", "react native",
                 "flutter app", "app store", "play store", "push notifications",
                 "mobile sdk", "mobile app"],
        "medium": ["smartphone", "tablet", "mobile users", "offline mode",
                   "cross-platform"],
    },
    "API/Backend": {
        "high": ["rest api", "restful", "graphql api", "microservices",
                 "api gateway", "webhook", "event-driven", "message queue",
                 "backend service"],
        "medium": ["endpoint", "api documentation", "api consumers", "headless",
                   "api", "backend", "web service"],
    },
    "ML/AI System": {
        "high": ["machine learning", "deep learning", "neural network", "ai model",
                 "natural language processing", "computer vision",
                 "recommendation engine", "training pipeline", "model inference",
                 "llm", "data science", "predictive analytics",
                 "classification model"],
        "medium": ["prediction", "automation", "intelligent", "ai-powered",
                   "ml pipeline", "ai system"],
    },
    "Data Platform": {
        "high": ["data warehouse", "data lake", "etl pipeline", "data pipeline",
                 "business intelligence", "analytics platform",
                 "data ingestion", "data processing", "olap"],
        "medium": ["reporting", "data visualization", "metrics", "kpis",
                   "analytics", "big data", "data platform"],
    },
    "Enterprise Software": {
        "high": ["erp", "crm", "hrms", "enterprise system",
                 "workflow automation", "business process", "approval workflow",
                 "role-based access", "multi-tenant", "b2b", "saas platform"],
        "medium": ["enterprise", "organization-wide", "department", "legacy modernization",
                   "supply chain", "hrm"],
    },
}

COMPLEXITY_SIGNALS_HIGH: list[str] = [
    "machine learning", "ai", "neural network", "deep learning",
    "real-time", "websocket", "event streaming", "kafka",
    "microservices", "service mesh", "distributed system",
    "blockchain", "smart contract",
    "computer vision", "nlp", "llm", "gpt",
    "embedded", "iot", "firmware",
    "high availability", "fault tolerant", "99.99%",
    "multi-region", "global cdn", "edge computing",
    "payment processing", "pci-dss", "pci dss",
    "hipaa", "soc2", "iso27001", "regulatory compliance",
]

COMPLEXITY_SIGNALS_LOW: list[str] = [
    "simple", "basic", "prototype", "mvp", "proof of concept",
    "minimal", "straightforward", "landing page", "static",
    "poc", "small",
]

METHODOLOGY_KEYWORDS: dict[str, list[str]] = {
    "Agile": [
        "agile", "scrum", "sprint", "kanban", "story points", "user stories",
        "backlog", "iteration", "standup", "retrospective", "velocity",
        "product owner", "scrum master", "epic", "two-week sprint",
    ],
    "Waterfall": [
        "waterfall", "sequential", "phase-based", "requirements phase",
        "design phase", "milestones", "deliverables", "sign-off",
        "formal review", "phase gate", "work breakdown structure", "wbs",
        "stage gate",
    ],
    "Hybrid": [
        "hybrid", "scrumban", "disciplined agile", "safe", "scaled agile",
        "wagile",
    ],
}

DURATION_WORDS: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "fifteen": 15, "eighteen": 18,
    "twenty": 20, "twenty-four": 24, "thirty-six": 36,
}

NUMBER_WORDS: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# Known external services for integration detection
EXTERNAL_SERVICES: list[str] = [
    "stripe", "paypal", "razorpay", "braintree", "square",
    "twilio", "sendgrid", "mailgun", "ses", "sns",
    "google maps", "mapbox",
    "aws s3", "cloudinary", "azure blob",
    "firebase", "supabase", "auth0", "cognito",
    "slack", "teams", "discord", "telegram", "whatsapp",
    "salesforce", "hubspot", "zoho",
    "google analytics", "segment", "mixpanel", "amplitude",
    "sentry", "datadog", "new relic",
    "openai", "anthropic", "gemini",
    "jira", "github", "gitlab",
]


# ══════════════════════════════════════════════════════════════════════
# NLP Extractor Class
# ══════════════════════════════════════════════════════════════════════

class NLPExtractor:
    """
    Industrial-grade SRS document parameter extractor.

    Uses a 4-strategy cascade:
    1. Structural analysis — tables, headers, lists
    2. Section-aware — extract within identified sections
    3. Global patterns — regex across full text
    4. Cross-validation — pick highest confidence
    """

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

        # Step 1: Preprocess into structured document
        doc = self._preprocess(text)

        # Step 2: Run all extractors (order matters — some depend on others)
        tech_stack = self._extract_tech_stack(doc)
        feature_count = self._count_features(doc)
        complexity = self._estimate_complexity(
            doc, tech_stack.value, feature_count.value
        )
        project_type = self._extract_project_type(doc, tech_stack.value)

        extracted = {
            "project_type": project_type.to_dict(),
            "tech_stack": tech_stack.to_dict(),
            "team_size": self._extract_team_size(doc).to_dict(),
            "duration_months": self._extract_duration(doc).to_dict(),
            "complexity": complexity.to_dict(),
            "methodology": self._extract_methodology(doc).to_dict(),
            "feature_count": feature_count.to_dict(),
            "project_name": self._extract_project_name(doc).to_dict(),
            "integration_count": self._extract_integration_count(doc).to_dict(),
            "volatility_score": self._estimate_volatility(doc).to_dict(),
            "team_experience": self._estimate_team_experience(doc).to_dict(),
        }

        logger.info(
            "nlp_extraction_complete",
            project_type=extracted["project_type"]["value"],
            complexity=extracted["complexity"]["value"],
            features=extracted["feature_count"]["value"],
            tech_count=len(extracted["tech_stack"]["value"]),
            integrations=extracted["integration_count"]["value"],
        )
        return extracted

    # ── Preprocessing ──────────────────────────────────────────────

    def _preprocess(self, text: str) -> DocumentStructure:
        """Build a structured representation of the document."""
        lines = text.split("\n")
        text_lower = text.lower()
        headers: list[dict] = []
        tables: list[str] = []
        list_items: list[str] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # Detect headers
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                header_text = stripped.lstrip("# ").strip()
                if header_text:
                    headers.append({"level": level, "text": header_text, "line_num": i})
            elif stripped.isupper() and 3 < len(stripped) < 80 and not stripped.startswith("|"):
                headers.append({"level": 1, "text": stripped, "line_num": i})
            elif re.match(r"^(?:section\s+)?\d+(?:\.\d+)*\s+[A-Z]", stripped, re.IGNORECASE):
                headers.append({"level": 2, "text": stripped, "line_num": i})

            # Detect table rows
            if "|" in stripped and stripped.count("|") >= 2:
                # Skip separator rows like |---|---|
                if not re.match(r"^\|[\s\-:|]+\|$", stripped):
                    tables.append(stripped)

            # Detect list items
            if re.match(r"^\s*[-•*]\s+\w", stripped):
                list_items.append(stripped.lstrip("-•* "))
            elif re.match(r"^\s*\d+[.)]\s+\w", stripped):
                list_items.append(re.sub(r"^\s*\d+[.)]\s+", "", stripped))
            elif re.match(r"^\s*[a-z][.)]\s+\w", stripped):
                list_items.append(re.sub(r"^\s*[a-z][.)]\s+", "", stripped))

        # Build sections map
        sections: dict[str, str] = {}
        for idx, header in enumerate(headers):
            start_line = header["line_num"] + 1
            end_line = headers[idx + 1]["line_num"] if idx + 1 < len(headers) else len(lines)
            body = "\n".join(lines[start_line:end_line]).strip()
            if body:
                sections[header["text"].lower()] = body

        return DocumentStructure(
            full_text=text,
            text_lower=text_lower,
            raw_lines=lines,
            headers=headers,
            tables=tables,
            list_items=list_items,
            sections=sections,
            word_count=len(text.split()),
        )

    # ── Default Extraction ─────────────────────────────────────────

    def _default_extraction(self) -> dict:
        """Return safe defaults when text is empty/too short."""
        defaults = {
            "project_type": ExtractionResult("Web App", 0.2, strategy="default"),
            "tech_stack": ExtractionResult([], 0.1, strategy="default"),
            "team_size": ExtractionResult(5, 0.2, strategy="default"),
            "duration_months": ExtractionResult(6.0, 0.2, strategy="default"),
            "complexity": ExtractionResult("Medium", 0.2, strategy="default"),
            "methodology": ExtractionResult("Agile", 0.2, strategy="default"),
            "feature_count": ExtractionResult(10, 0.2, strategy="default"),
            "project_name": ExtractionResult("", 0.0, strategy="default"),
            "integration_count": ExtractionResult(2, 0.1, strategy="default"),
            "volatility_score": ExtractionResult(3, 0.1, strategy="default"),
            "team_experience": ExtractionResult(2.0, 0.1, strategy="default"),
        }
        return {k: v.to_dict() for k, v in defaults.items()}

    # ── Project Name ───────────────────────────────────────────────

    def _extract_project_name(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Extract project name from document structure.
        NEVER uses the filename. Returns empty string if nothing found.
        """
        patterns = [
            # Explicit labels — stop at newline, period, or comma
            (r"(?:project\s+name|system\s+name|application\s+name|product\s+name|title)"
             r"\s*[:\-–]\s*[\"']?([\w][\w \-\.]{2,60}?)(?:\n|\r|\.|\,|$)", 0.95),
            # Markdown heading with system/app suffix
            (r"(?:^|\n)#{1,3}\s+([A-Z][\w\s]{3,40}?)\s*(?:system|application|platform|portal|app|project)",
             0.85),
            # "Proposal for ...", "Estimation for ..."
            (r"(?:proposal\s+for|estimation\s+for|specification\s+for|requirements\s+for|quote\s+for)"
             r"\s+(?:the\s+)?([\w][\w\s]{2,50}?)(?:\.|\n|$)", 0.80),
            # SRS/PRD heading: "XYZ SRS" or "XYZ Requirements Specification"
            (r"(?:^|\n)([A-Z][\w\s]{3,40}?)\s*(?:SRS|PRD|BRD|specification|requirements\s+document)",
             0.75),
            # Simple "Project Name: ..." with quotes
            (r"project\s*(?:name|title)?\s*:\s*[\"']?([A-Z][A-Za-z0-9\s\-]{2,30})", 0.70),
            # First markdown heading
            (r"^#\s+(.{3,50})$", 0.60),
        ]

        for pattern, conf in patterns:
            match = re.search(pattern, doc.full_text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = match.group(1).strip().rstrip(".,;:")
                # Strip document type suffixes
                for suffix in ["SRS", "PRD", "BRD", "Requirements", "Specification", "Document"]:
                    name = re.sub(rf"\s*{suffix}\s*$", "", name, flags=re.IGNORECASE).strip()
                if 2 < len(name) <= 80 and not name.lower().startswith(("http", "www", "file")):
                    return ExtractionResult(
                        value=name[:80], confidence=conf,
                        evidence=[match.group(0).strip()[:100]],
                        strategy="pattern",
                    )

        return ExtractionResult(value="", confidence=0.0, strategy="fallback")

    # ── Project Type ───────────────────────────────────────────────

    def _extract_project_type(
        self, doc: DocumentStructure, tech_stack: list[str]
    ) -> ExtractionResult:
        """Classify project type using multi-signal scoring."""
        scores: dict[str, float] = {}

        for ptype, signals in PROJECT_TYPE_SIGNALS.items():
            score = 0.0
            for kw in signals.get("high", []):
                if kw in doc.text_lower:
                    score += 3.0
            for kw in signals.get("medium", []):
                if kw in doc.text_lower:
                    score += 1.0
            if score > 0:
                scores[ptype] = score

        # Tech stack boosting
        tech_lower = {t.lower() for t in tech_stack}
        ml_techs = {"machine learning", "pytorch", "tensorflow", "xgboost",
                     "scikit-learn", "deep learning", "neural network"}
        mobile_techs = {"react native", "flutter", "swift", "kotlin",
                        "android", "ios", "expo"}

        if ml_techs & tech_lower:
            scores["ML/AI System"] = scores.get("ML/AI System", 0) + 4.0
        if mobile_techs & tech_lower:
            scores["Mobile App"] = scores.get("Mobile App", 0) + 4.0

        if scores:
            best = max(scores, key=scores.get)  # type: ignore[arg-type]
            sorted_scores = sorted(scores.values(), reverse=True)
            second = sorted_scores[1] if len(sorted_scores) > 1 else 0
            confidence = min(0.95, scores[best] / (scores[best] + second + 1))
            return ExtractionResult(
                value=best, confidence=confidence, strategy="scoring"
            )

        return ExtractionResult(value="Web App", confidence=0.3, strategy="fallback")

    # ── Tech Stack ─────────────────────────────────────────────────

    def _extract_tech_stack(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Extract ALL mentioned technologies from document.
        Scans tables, sections, lists, and prose separately.
        """
        found: list[str] = []
        evidence: list[str] = []

        # Ambiguous keywords that match common English words —
        # only accept these from tech-related sections
        AMBIGUOUS_TECHS = {
            "less", "go", "helm", "render", "dart", "hono", "bun",
            "solid.js", "expo", "ionic", "lambda", "remix",
        }

        # Combine search targets: full text + table rows + list items
        search_texts = [doc.text_lower]

        # Also search in technology-related sections specifically
        tech_section_text = ""
        for header_key, body in doc.sections.items():
            if any(kw in header_key for kw in [
                "technology", "tech stack", "tools", "framework", "architecture",
                "platform", "infrastructure", "dependencies", "libraries", "stack",
                "technical"
            ]):
                search_texts.append(body.lower())
                tech_section_text += " " + body.lower()
                if len(evidence) < 3:
                    evidence.append(f"Section: {header_key[:60]}")

        combined_text = " ".join(search_texts)

        # Sort keywords by length descending so multi-word matches go first
        sorted_keywords = sorted(ALL_TECH_KEYWORDS, key=len, reverse=True)

        for tech in sorted_keywords:
            pattern = r"\b" + re.escape(tech) + r"\b"

            # For ambiguous words, only match in tech-related sections
            if tech.lower() in AMBIGUOUS_TECHS:
                if tech_section_text and re.search(pattern, tech_section_text, re.IGNORECASE):
                    found.append(tech)
                continue

            if re.search(pattern, combined_text, re.IGNORECASE):
                found.append(tech)

        # Deduplicate using display names
        seen_display: set[str] = set()
        unique: list[str] = []
        for t in found:
            t_lower = t.lower()
            display = TECH_DISPLAY_NAMES.get(t_lower)
            if display is None:
                display = t.title() if len(t) > 3 else t.upper()
            if display not in seen_display:
                seen_display.add(display)
                unique.append(display)

        confidence = min(0.95, 0.3 + len(unique) * 0.07) if unique else 0.2
        return ExtractionResult(
            value=unique[:25], confidence=confidence,
            evidence=evidence[:3], strategy="multi_source",
        )

    # ── Team Size ──────────────────────────────────────────────────

    def _extract_team_size(self, doc: DocumentStructure) -> ExtractionResult:
        """Extract team/headcount size from document."""

        # Strategy 1: Explicit labels
        explicit_patterns = [
            r"(?:team\s+size|headcount|staff\s+count|resource\s+count)\s*[:\-–]\s*(\d{1,3})",
            r"(?:team\s+of|squad\s+of|group\s+of|crew\s+of)\s+(\d{1,3})",
            r"(\d{1,3})\s+(?:FTE|full.time\s+equivalent|resources|personnel)",
            r"team\s*(?:size)?\s*:?\s*(\d{1,3})\b",
        ]
        for pattern in explicit_patterns:
            m = re.search(pattern, doc.text_lower)
            if m:
                size = int(m.group(1))
                if 1 <= size <= 200:
                    return ExtractionResult(
                        value=size, confidence=0.85,
                        evidence=[m.group(0).strip()[:80]],
                        strategy="explicit_label",
                    )

        # Strategy 2: Staffing table — sum role counts from table rows
        role_pattern = re.compile(
            r"(\d+)\s*(?:x\s+)?(?:developer|engineer|architect|designer|tester|qa|"
            r"analyst|manager|admin|devops|lead|pm|scrum|frontend|backend|fullstack|"
            r"full-stack|data\s+scientist|ml\s+engineer)",
            re.IGNORECASE,
        )
        table_total = 0
        for row in doc.tables:
            for m in role_pattern.finditer(row):
                n = int(m.group(1))
                if 1 <= n <= 50:
                    table_total += n
        if table_total > 0:
            return ExtractionResult(
                value=min(table_total, 200), confidence=0.90,
                evidence=["Summed from staffing table"],
                strategy="staffing_table",
            )

        # Strategy 3: Individual role mentions in prose
        role_mentions = []
        individual_patterns = [
            r"(\d+)\s+developers?",
            r"(\d+)\s+engineers?",
            r"(\d+)\s+designers?",
            r"(\d+)\s+testers?",
            r"(\d+)\s+(?:qa|quality)",
            r"(\d+)\s+(?:pm|project\s+manager)",
            r"(\d+)\s+(?:person|people|members?|staff)",
        ]
        for pattern in individual_patterns:
            for m in re.finditer(pattern, doc.text_lower):
                n = int(m.group(1))
                if 1 <= n <= 100:
                    role_mentions.append(n)

        if role_mentions:
            total = sum(role_mentions)
            if 1 <= total <= 200:
                return ExtractionResult(
                    value=total, confidence=0.75,
                    evidence=[f"Sum of {len(role_mentions)} role mentions"],
                    strategy="role_sum",
                )

        # Strategy 4: Written-out numbers
        for word, num in NUMBER_WORDS.items():
            if re.search(
                rf"\b{word}\s+(?:person|developer|engineer|member|people)", doc.text_lower
            ):
                return ExtractionResult(
                    value=num, confidence=0.60,
                    evidence=[f"Written number: '{word}'"],
                    strategy="word_number",
                )

        # Strategy 5: Heuristic phrases
        heuristic_phrases = {
            "two-pizza team": 6, "small team": 4, "large team": 15,
            "medium team": 8, "cross-functional team": 8,
        }
        for phrase, size in heuristic_phrases.items():
            if phrase in doc.text_lower:
                return ExtractionResult(
                    value=size, confidence=0.45,
                    evidence=[f"Heuristic: '{phrase}'"],
                    strategy="heuristic",
                )

        return ExtractionResult(value=5, confidence=0.2, strategy="default")

    # ── Duration ───────────────────────────────────────────────────

    def _extract_duration(self, doc: DocumentStructure) -> ExtractionResult:
        """Extract project duration in months."""

        # Strategy 1: Explicit months
        month_patterns = [
            r"(\d+)\s*[-–]?\s*months?\s*(?:project|engagement|timeline|period|duration|delivery)",
            r"(?:duration|timeline|period)\s*[:\-–]\s*(\d+)\s*months?",
            r"(\d+)\s*[-–]?\s*months?",
        ]
        for pattern in month_patterns:
            m = re.search(pattern, doc.text_lower)
            if m:
                months = float(m.group(1))
                if 0.5 <= months <= 60:
                    return ExtractionResult(
                        value=round(months, 1), confidence=0.85,
                        evidence=[m.group(0).strip()[:80]],
                        strategy="explicit_months",
                    )

        # Strategy 2: Explicit weeks
        week_patterns = [
            r"(\d+)\s*[-–]?\s*weeks?\s*(?:project|engagement|timeline|duration)",
            r"(\d+)\s*weeks?\s+(?:total|duration|timeline)",
            r"(\d+)\s*[-–]?\s*weeks?",
        ]
        for pattern in week_patterns:
            m = re.search(pattern, doc.text_lower)
            if m:
                weeks = float(m.group(1))
                months = round(weeks / 4.33, 1)
                if 0.5 <= months <= 60:
                    return ExtractionResult(
                        value=months, confidence=0.80,
                        evidence=[m.group(0).strip()[:80]],
                        strategy="explicit_weeks",
                    )

        # Strategy 3: Written-out months
        for word, num in DURATION_WORDS.items():
            if re.search(rf"\b{word}\s+months?", doc.text_lower):
                return ExtractionResult(
                    value=float(num), confidence=0.75,
                    evidence=[f"Written: '{word} months'"],
                    strategy="word_months",
                )

        # Strategy 4: Quarter-based
        quarter_match = re.search(
            r"(?:deliver|launch|release|go.live|complete)\s+(?:by\s+)?Q([1-4])\s+(\d{4})",
            doc.text_lower,
        )
        if quarter_match:
            q = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            # Approximate months from 2026-04 to target quarter end
            target_month = q * 3
            months_from_now = (year - 2026) * 12 + target_month - 4
            if 0.5 <= months_from_now <= 60:
                return ExtractionResult(
                    value=round(months_from_now, 1), confidence=0.70,
                    evidence=[quarter_match.group(0).strip()[:80]],
                    strategy="quarter_based",
                )

        # Strategy 5: Sprint-based
        sprint_match = re.search(r"(\d+)\s+(?:two.week\s+)?sprints?", doc.text_lower)
        if sprint_match:
            sprints = float(sprint_match.group(1))
            months = round(sprints * 2 / 4.33, 1)
            if 0.5 <= months <= 60:
                return ExtractionResult(
                    value=months, confidence=0.65,
                    evidence=[sprint_match.group(0).strip()[:80]],
                    strategy="sprint_based",
                )

        # Strategy 6: Days
        day_match = re.search(r"(\d+)\s*[-–]?\s*days?", doc.text_lower)
        if day_match:
            days = float(day_match.group(1))
            months = round(days / 30, 1)
            if 0.5 <= months <= 60:
                return ExtractionResult(
                    value=months, confidence=0.60,
                    evidence=[day_match.group(0).strip()[:80]],
                    strategy="days_based",
                )

        return ExtractionResult(value=6.0, confidence=0.2, strategy="default")

    # ── Complexity ─────────────────────────────────────────────────

    def _estimate_complexity(
        self, doc: DocumentStructure, tech_stack: list[str], feature_count: int,
    ) -> ExtractionResult:
        """Estimate project complexity using 20-point scoring system."""
        score = 0.0

        # Feature count contribution
        if feature_count <= 10:
            score += 0
        elif feature_count <= 25:
            score += 1
        elif feature_count <= 50:
            score += 2
        else:
            score += 3

        # Tech stack size
        tech_count = len(tech_stack)
        if tech_count <= 3:
            score += 0
        elif tech_count <= 7:
            score += 1
        elif tech_count <= 12:
            score += 2
        else:
            score += 3

        # High-complexity technology signals
        high_tech_count = 0
        for signal in COMPLEXITY_SIGNALS_HIGH:
            if signal in doc.text_lower:
                high_tech_count += 1
        score += min(4, high_tech_count)

        # Scale signals
        scale_keywords = [
            "millions of users", "10m+", "billion requests",
            "high throughput", "high concurrency", "low latency",
            "petabytes", "terabytes",
            "global deployment", "multi-tenant",
        ]
        scale_count = sum(1 for kw in scale_keywords if kw in doc.text_lower)
        score += min(3, scale_count)

        # Integration signals
        integration_keywords = ["third-party api", "external integration",
                                "erp integration", "third party"]
        integ_count = sum(1 for kw in integration_keywords if kw in doc.text_lower)
        score += min(2, integ_count * 0.5)

        # Explicit low signals (negative)
        low_count = sum(1 for kw in COMPLEXITY_SIGNALS_LOW if kw in doc.text_lower)
        score -= min(3, low_count)

        # Explicit high signals
        high_explicit = ["complex", "sophisticated", "enterprise-grade", "advanced",
                         "critical", "mission-critical", "large-scale"]
        high_count = sum(1 for kw in high_explicit if kw in doc.text_lower)
        score += min(3, high_count)

        # Word count as a signal
        if doc.word_count > 5000:
            score += 1
        if doc.word_count > 10000:
            score += 1

        # Map score to level
        if score <= 2:
            level, conf = "Low", 0.75
        elif score <= 5:
            level, conf = "Medium", 0.75
        elif score <= 9:
            level, conf = "High", 0.80
        else:
            level, conf = "Very High", 0.85

        return ExtractionResult(
            value=level, confidence=conf,
            evidence=[f"Complexity score: {score:.1f}"],
            strategy="scoring",
        )

    # ── Methodology ────────────────────────────────────────────────

    def _extract_methodology(self, doc: DocumentStructure) -> ExtractionResult:
        """Detect development methodology."""
        method_scores: dict[str, int] = {}

        for method, keywords in METHODOLOGY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in doc.text_lower)
            if count > 0:
                method_scores[method] = count

        # DevOps signals imply Agile
        devops_kw = ["ci/cd", "continuous integration", "continuous deployment",
                     "devops", "continuous delivery", "pipeline"]
        devops_count = sum(1 for kw in devops_kw if kw in doc.text_lower)

        if method_scores:
            if "Hybrid" in method_scores:
                return ExtractionResult(
                    value="Hybrid", confidence=0.85, strategy="keyword"
                )
            best = max(method_scores, key=method_scores.get)  # type: ignore[arg-type]
            confidence = min(0.85, method_scores[best] * 0.15)
            return ExtractionResult(
                value=best, confidence=confidence, strategy="keyword"
            )

        if devops_count > 0:
            return ExtractionResult(
                value="Agile", confidence=0.65,
                evidence=["DevOps signals imply Agile"],
                strategy="devops_inference",
            )

        return ExtractionResult(value="Agile", confidence=0.3, strategy="default")

    # ── Feature Count ──────────────────────────────────────────────

    def _count_features(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Count distinct user-facing features/requirements.
        Multi-strategy: section-based > list-based > explicit mention > keyword density.
        """

        # Strategy 1: Section-based counting (HIGHEST PRIORITY)
        section_keywords = [
            "functional requirements", "features", "use cases",
            "user stories", "user requirements", "system features",
            "functional specification", "feature list",
            "core features", "key features",
        ]
        section_count = 0
        for header_key, body in doc.sections.items():
            if any(kw in header_key for kw in section_keywords):
                # Count numbered sub-items
                numbered = len(re.findall(
                    r"(?:^|\n)\s*(?:\d+\.\d+|\d+\.|\w+-\d+|FR-\d+|US-\d+|UC-\d+)\s+\w",
                    body,
                ))
                # Count bullet items
                bullets = len(re.findall(r"(?:^|\n)\s*[-•*]\s+\w", body))
                section_count += max(numbered, bullets)

        if section_count >= 3:
            return ExtractionResult(
                value=min(section_count, 200), confidence=0.90,
                evidence=[f"Found in {len(section_keywords)} functional sections"],
                strategy="section_based",
            )

        # Strategy 2: Explicit count mentions
        feature_patterns = [
            r"(\d+)\s+(?:features?|user\s+stories?|requirements?|modules?|"
            r"use\s+cases?|functionalities?|epics?)",
            r"(?:total\s+of\s+)?(\d+)\s+(?:functional|system)\s+requirements?",
        ]
        explicit_counts: list[int] = []
        for pattern in feature_patterns:
            for m in re.finditer(pattern, doc.text_lower):
                n = int(m.group(1))
                if 1 <= n <= 200:
                    explicit_counts.append(n)

        if explicit_counts:
            count = max(explicit_counts)
            return ExtractionResult(
                value=count, confidence=0.80,
                evidence=[f"Explicit mention: {count}"],
                strategy="explicit_count",
            )

        # Strategy 3: List item counting across doc
        bullet_count = len(re.findall(r"(?:^|\n)\s*[-•*]\s+\w", doc.full_text))
        numbered_count = len(re.findall(r"(?:^|\n)\s*\d+[.)]\s+\w", doc.full_text))
        structural_count = bullet_count + numbered_count

        if structural_count > 3:
            return ExtractionResult(
                value=min(structural_count, 50), confidence=0.55,
                evidence=[f"Bullets: {bullet_count}, Numbered: {numbered_count}"],
                strategy="list_counting",
            )

        # Strategy 4: Keyword density heuristic
        action_phrases = [
            "the user can", "the system shall", "the system must",
            "the user should", "the system will", "the application shall",
            "users can", "users shall", "users must",
        ]
        action_count = sum(
            doc.text_lower.count(phrase) for phrase in action_phrases
        )
        if action_count > 0:
            estimated = max(5, int(action_count / 1.5))
            return ExtractionResult(
                value=min(estimated, 50), confidence=0.45,
                evidence=[f"Action phrases found: {action_count}"],
                strategy="keyword_density",
            )

        # Strategy 5: Feature mention count
        feature_mentions = len(re.findall(
            r"(?:feature|requirement|user story|functionality|capability)",
            doc.text_lower,
        ))
        if feature_mentions > 0:
            return ExtractionResult(
                value=max(feature_mentions, 5), confidence=0.40,
                strategy="feature_mentions",
            )

        return ExtractionResult(value=10, confidence=0.2, strategy="default")

    # ── Integration Count ──────────────────────────────────────────

    def _extract_integration_count(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Count external API/service integrations.
        Maps to IFPUG External Interface Files.
        """
        found_services: set[str] = set()

        for service in EXTERNAL_SERVICES:
            if re.search(r"\b" + re.escape(service) + r"\b", doc.text_lower):
                found_services.add(service)

        # Also count integration-related phrases
        integration_phrases = [
            "integrates with", "third-party", "external api",
            "webhook from", "connects to", "via api",
            "api integration", "third party integration",
        ]
        phrase_count = sum(1 for p in integration_phrases if p in doc.text_lower)

        # Combine: known services + inferred from phrases
        total = len(found_services) + max(0, phrase_count - len(found_services))
        total = max(total, 2)  # Minimum 2 (every project has some)
        total = min(total, 30)

        confidence = min(0.85, 0.3 + len(found_services) * 0.1)
        return ExtractionResult(
            value=total, confidence=confidence,
            evidence=[f"Services: {', '.join(list(found_services)[:5])}"] if found_services else [],
            strategy="service_detection",
        )

    # ── Volatility Score ───────────────────────────────────────────

    def _estimate_volatility(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Estimate requirements volatility (1-5 scale).
        1=stable, 5=highly volatile.
        """
        high_signals = [
            "subject to change", "tbd", "to be determined", "to be decided",
            "agile refinement", "evolving requirements", "future phases",
            "mvp first", "iterative", "stakeholder feedback",
            "may change", "flexible scope", "ongoing refinement",
            "phased approach", "incremental",
        ]
        low_signals = [
            "fixed scope", "hard requirement", "cannot change",
            "regulatory requirement", "iso standard", "contractual obligation",
            "non-negotiable", "mandatory", "compliance requirement",
            "fixed price", "locked scope",
        ]

        high_count = sum(1 for s in high_signals if s in doc.text_lower)
        low_count = sum(1 for s in low_signals if s in doc.text_lower)

        if low_count > high_count + 2:
            score = 1
        elif low_count > high_count:
            score = 2
        elif high_count <= 1:
            score = 3  # neutral default
        elif high_count <= 3:
            score = 4
        else:
            score = 5

        confidence = 0.50 if high_count + low_count == 0 else 0.70
        return ExtractionResult(
            value=score, confidence=confidence,
            evidence=[f"High volatility signals: {high_count}, Low: {low_count}"],
            strategy="signal_counting",
        )

    # ── Team Experience ────────────────────────────────────────────

    def _estimate_team_experience(self, doc: DocumentStructure) -> ExtractionResult:
        """
        Estimate team experience level (1-4 scale).
        1=junior, 2=mixed, 3=experienced, 4=expert.
        """
        high_signals = [
            "senior engineers", "experienced team", "10+ years",
            "principal", "staff engineer", "cto", "tech lead",
            "senior developers", "expert team", "seasoned",
            "lead engineer", "architect", "highly experienced",
            "years of experience",
        ]
        low_signals = [
            "junior", "fresh graduates", "entry level", "entry-level",
            "interns", "new team", "small startup", "bootcamp",
            "learning curve", "ramp-up time", "training required",
        ]

        high_count = sum(1 for s in high_signals if s in doc.text_lower)
        low_count = sum(1 for s in low_signals if s in doc.text_lower)

        if high_count >= 3:
            level = 4.0
        elif high_count > low_count:
            level = 3.0
        elif low_count > high_count:
            level = 1.0
        else:
            level = 2.0  # mixed/unknown default

        confidence = 0.40 if high_count + low_count == 0 else 0.65
        return ExtractionResult(
            value=level, confidence=confidence,
            evidence=[f"Senior signals: {high_count}, Junior: {low_count}"],
            strategy="signal_counting",
        )


# ══════════════════════════════════════════════════════════════════════
# Singleton
# ══════════════════════════════════════════════════════════════════════

nlp_extractor = NLPExtractor()
