import json
from dataclasses import dataclass

import pytest


class FakeWebSearchService:
    def __init__(self, result_template: str | None = None) -> None:
        self.result_template = result_template or (
            "Title: Example Result\n"
            "URL: https://example.com\n"
            "Short summary: Example search result summary."
        )
        self.queries: list[str] = []

    def search(self, query: str) -> str:
        self.queries.append(query)
        return f"Query Source: {query}\n{self.result_template}"


class FakeImageGenerator:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_image(self, prompt: str) -> bytes:
        self.prompts.append(prompt)
        return b"fake-image-bytes"


@dataclass
class FakeImageGeneratorFactory:
    instances: list[FakeImageGenerator]

    def __call__(self) -> FakeImageGenerator:
        instance = FakeImageGenerator()
        self.instances.append(instance)
        return instance


@pytest.fixture
def product_requirements_output() -> str:
    return (
        "REQUIREMENTS_READY\n\n"
        "Audience personas:\n"
        "- Retail crypto beginners seeking plain-English education\n"
        "- Investors comparing digital assets for long-term allocation\n\n"
        "Pain points:\n"
        "- Confusing terminology\n"
        "- Lack of trustworthy explanations\n\n"
        "Value proposition:\n"
        "- Clear, trustworthy guides to digital assets\n\n"
        "Key services/products:\n"
        "- Educational articles\n"
        "- Market explainers\n\n"
        "Conversion goals:\n"
        "- Newsletter signup\n"
        "- Resource downloads\n\n"
        "Messaging pillars:\n"
        "- Clarity\n"
        "- Credibility\n"
        "- Practicality\n\n"
        "Functional requirements:\n"
        "- Homepage\n"
        "- Topic pages\n"
        "- Responsive layout\n\n"
        "Tone and brand personality:\n"
        "- Confident, educational, accessible"
    )


@pytest.fixture
def research_scope_output() -> str:
    return json.dumps(
        {
            "primary_topic": "cryptocurrency",
            "personas": [
                "Retail crypto beginners",
                "Self-directed investors",
            ],
            "pain_points": [
                "Confusing terminology",
                "Difficulty comparing assets",
            ],
            "knowledge_topics": [
                "history of bitcoin",
                "how blockchain works",
                "major cryptocurrencies",
                "adoption and use cases",
                "key events in the crypto ecosystem",
            ],
        }
    )


@pytest.fixture
def strategic_queries_output() -> str:
    return "\n".join(
        [
            "top cryptocurrency education website homepage examples",
            "best cryptocurrency website hero section messaging patterns",
            "high-converting cryptocurrency website call to action patterns",
            "cryptocurrency SEO keyword clusters",
            "cryptocurrency website differentiation strategy examples",
        ]
    )


@pytest.fixture
def knowledge_queries_output() -> str:
    return "\n".join(
        [
            "cryptocurrency overview and history",
            "how cryptocurrency works",
            "major cryptocurrency examples and categories",
            "cryptocurrency adoption and use cases",
            "key events and milestones in cryptocurrency",
        ]
    )


@pytest.fixture
def research_output_json() -> str:
    return json.dumps(
        {
            "strategic_insights": {
                "competitor_patterns": [
                    "Competitors emphasize trust, plain-language navigation, and educational hero sections."
                ],
                "seo_keywords": [
                    "bitcoin explained",
                    "how blockchain works",
                    "crypto adoption use cases",
                ],
                "messaging_patterns": [
                    "Clear educational framing supported by concise proof points and newsletter CTAs."
                ],
            },
            "knowledge_base": {
                "topics": [
                    {
                        "topic": "History of Bitcoin",
                        "summary": "Bitcoin emerged from the 2008 financial crisis and launched in 2009 as a decentralized digital currency.",
                        "key_points": [
                            "The Bitcoin white paper was published in 2008.",
                            "The network launched in January 2009.",
                        ],
                        "facts": [
                            "Satoshi Nakamoto published the Bitcoin white paper in 2008.",
                            "The genesis block was mined in 2009.",
                        ],
                        "sources": [
                            "https://bitcoin.org/bitcoin.pdf",
                            "https://www.investopedia.com/terms/b/bitcoin.asp",
                        ],
                    },
                    {
                        "topic": "How Blockchain Works",
                        "summary": "Blockchains store transactions in linked blocks that are verified by a distributed network rather than a single institution.",
                        "key_points": [
                            "Blocks are linked with cryptographic hashes.",
                            "Consensus mechanisms help participants agree on valid transactions.",
                        ],
                        "facts": [
                            "A blockchain is a distributed ledger shared across participating nodes.",
                            "New blocks reference previous blocks to preserve ledger history.",
                        ],
                        "sources": [
                            "https://www.ibm.com/think/topics/blockchain",
                        ],
                    },
                ]
            },
        }
    )


@pytest.fixture
def site_structure_json() -> str:
    return json.dumps(
        {
            "site_structure": {
                "pages": [
                    {
                        "slug": "/",
                        "title": "Crypto Explained",
                        "page_goal": "Help visitors understand digital assets and trust the brand as an educational resource.",
                        "sections": [
                            {
                                "heading": "What Bitcoin Introduced",
                                "text": "Bitcoin introduced a decentralized digital currency model that allows peer-to-peer transfers without a central bank controlling issuance or settlement.",
                                "supporting_points": [
                                    "The Bitcoin white paper was published in 2008.",
                                    "The network launched in January 2009.",
                                ],
                            },
                            {
                                "heading": "Why Blockchain Matters",
                                "text": "Blockchain networks keep a shared ledger across many participants, allowing transactions to be verified collectively instead of by a single institution.",
                                "supporting_points": [
                                    "Blocks are linked with cryptographic hashes.",
                                    "Consensus mechanisms help validate transactions.",
                                ],
                            },
                        ],
                    }
                ]
            }
        }
    )


@pytest.fixture
def architecture_spec_json() -> str:
    return json.dumps(
        {
            "architecture_spec": {
                "project_structure": [
                    "index.html",
                    "css/styles.css",
                    "js/main.js",
                    "assets/images/",
                ],
                "components": [
                    "site-header",
                    "hero-section",
                    "content-section",
                    "site-footer",
                ],
                "css_strategy": "Single stylesheet organized by layout, components, and responsive overrides using CSS custom properties.",
                "javascript_strategy": "Single main.js file for small interactive behavior such as mobile navigation.",
                "asset_structure": [
                    "assets/images/hero.png",
                    "assets/images/blockchain.png",
                    "assets/images/adoption.png",
                ],
            }
        }
    )


@pytest.fixture
def design_spec_json() -> str:
    return json.dumps(
        {
            "design_system": {
                "color_palette": {
                    "primary": "#0f172a",
                    "secondary": "#1e293b",
                    "accent": "#38bdf8",
                    "background": "#f8fafc",
                    "surface": "#ffffff",
                    "text_primary": "#0f172a",
                    "text_secondary": "#475569",
                },
                "typography": {
                    "heading_font": "Roboto Slab",
                    "body_font": "Open Sans",
                    "scale": {
                        "h1": "48px",
                        "h2": "36px",
                        "h3": "28px",
                        "body": "18px",
                    },
                },
                "spacing_system": {
                    "base_unit": "8px",
                    "section_padding": "64px",
                    "container_width": "1200px",
                },
                "layout_rules": {
                    "grid": "12-column",
                    "max_width": "1200px",
                    "responsive_breakpoints": ["1024px", "768px"],
                },
                "components": {
                    "navbar": "Top navigation with links and CTA.",
                    "hero_section": "Editorial hero with title, summary, and featured image.",
                    "feature_cards": "Two-column educational content blocks.",
                    "cta_section": "Newsletter signup banner.",
                    "footer": "Compact footer with trust links.",
                },
            },
            "images": [
                {
                    "filename": "hero.png",
                    "prompt": "Editorial hero illustration about cryptocurrency education",
                    "alt": "Illustration representing cryptocurrency education",
                },
                {
                    "filename": "blockchain.png",
                    "prompt": "Diagram-style illustration of blockchain validation",
                    "alt": "Illustration showing how blockchain works",
                },
                {
                    "filename": "adoption.png",
                    "prompt": "Modern illustration about cryptocurrency adoption and real-world use cases",
                    "alt": "Illustration of cryptocurrency adoption use cases",
                },
            ],
        }
    )


@pytest.fixture
def development_tasks_json() -> str:
    return json.dumps(
        {
            "tasks": [
                {
                    "id": "task-1",
                    "description": "Create the page scaffold and semantic sections for the homepage.",
                    "files_involved": ["index.html"],
                },
                {
                    "id": "task-2",
                    "description": "Implement the design system in the stylesheet.",
                    "files_involved": ["css/styles.css"],
                },
                {
                    "id": "task-3",
                    "description": "Add mobile navigation behavior in JavaScript.",
                    "files_involved": ["js/main.js"],
                },
            ]
        }
    )


@pytest.fixture
def generated_files_json() -> str:
    return json.dumps(
        {
            "files": {
                "index.html": (
                    "<!DOCTYPE html>"
                    "<html lang='en'>"
                    "<head>"
                    "<meta charset='UTF-8'>"
                    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                    "<title>Crypto Explained</title>"
                    "<link rel='stylesheet' href='css/styles.css'>"
                    "</head>"
                    "<body>"
                    "<header class='site-header'><h1>Crypto Explained</h1></header>"
                    "<main>"
                    "<section><h2>What Bitcoin Introduced</h2>"
                    "<p>Bitcoin introduced a decentralized digital currency model that allows peer-to-peer transfers without a central bank controlling issuance or settlement.</p>"
                    "<ul><li>The Bitcoin white paper was published in 2008.</li><li>The network launched in January 2009.</li></ul>"
                    "</section>"
                    "<section><h2>Why Blockchain Matters</h2>"
                    "<p>Blockchain networks keep a shared ledger across many participants, allowing transactions to be verified collectively instead of by a single institution.</p>"
                    "<ul><li>Blocks are linked with cryptographic hashes.</li><li>Consensus mechanisms help validate transactions.</li></ul>"
                    "</section>"
                    "<img src='assets/images/hero.png' alt='Illustration representing cryptocurrency education'>"
                    "</main>"
                    "<script src='js/main.js'></script>"
                    "</body></html>"
                ),
                "css/styles.css": (
                    ":root { --color-primary: #0f172a; --color-accent: #38bdf8; }"
                    "body { margin: 0; color: var(--color-primary); }"
                ),
                "js/main.js": "document.addEventListener('DOMContentLoaded', () => {});",
            }
        }
    )


@pytest.fixture
def qa_approved_feedback() -> str:
    return "- HTML structure is valid.\n- Content is rendered correctly.\nAPPROVED"


@pytest.fixture
def devops_output() -> str:
    return "1. Build the container.\n2. Run the container locally."


@pytest.fixture
def fake_image_generator_factory() -> FakeImageGeneratorFactory:
    return FakeImageGeneratorFactory(instances=[])


@pytest.fixture
def fake_web_search_service() -> FakeWebSearchService:
    return FakeWebSearchService()


def assert_product_requirements_document(output: str) -> None:
    required_sections = [
        "REQUIREMENTS_READY",
        "Audience personas",
        "Pain points",
        "Value proposition",
        "Key services/products",
        "Conversion goals",
        "Messaging pillars",
        "Functional requirements",
        "Tone and brand personality",
    ]
    for section in required_sections:
        assert section in output
