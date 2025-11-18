# Changelog

This changelog contains the notable updates to the **Context Enginnering for Multi-Agent Systems** repository.   
🐬 Indicates *new bonus notebooks* to explore.


## [November 18, 2025]

### Chapter09/Marketing_Assistant.ipynb
### Fixed
- **Moderation API Type:** Resolved a critical formatting issue in `Marketing_Assistant.ipynb` (Cell 4) where the OpenAI Moderation API failed with `Error code: 400` when agents returned structured data (dictionaries or lists). Added logic to serialize these outputs into strings before submission.

### Added
- **JSON Support:** Added `import json` to the execution cell to support data serialization.

### Changed
- **Output Rendering:** Updated the `execute_and_display` function to detect JSON outputs and render them as formatted Markdown code blocks for improved readability in the notebook.

## [November 7, 2025]

Repository made public.
