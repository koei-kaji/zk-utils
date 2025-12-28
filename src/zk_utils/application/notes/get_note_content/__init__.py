from pathlib import Path
from typing import Any

from injector import inject, singleton
from markdown_it import MarkdownIt

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService


class GetNoteContentInput(ABCInput):
    path: Path
    headings: list[str] | None = None


class GetNoteContentOutput(ABCOutput):
    content: str
    headings: list[str]


@singleton
class GetNoteContentService(ABCService[GetNoteContentInput, GetNoteContentOutput]):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: GetNoteContentInput) -> GetNoteContentOutput:
        note = self._repository.find_note_content(input_data.path)
        content = note.content or ""

        # マークダウンをパースしてh2見出しを抽出
        md = MarkdownIt()
        tokens = md.parse(content)

        # h2見出しのリストを作成
        h2_headings = []
        for i, token in enumerate(tokens):
            if token.type == "heading_open" and token.tag == "h2":
                # 次のトークンがinlineでその内容が見出しテキスト
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    h2_headings.append(tokens[i + 1].content)

        # 指定された見出しのセクションを抽出
        if input_data.headings:
            extracted_content = self._extract_heading_sections(
                tokens, input_data.headings
            )
            return GetNoteContentOutput(content=extracted_content, headings=h2_headings)

        return GetNoteContentOutput(content=content, headings=h2_headings)

    def _extract_heading_sections(
        self, tokens: list[Any], target_headings: list[str]
    ) -> str:
        """指定された見出しのセクションを抽出"""
        sections = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # h2見出しを見つける
            if token.type == "heading_open" and token.tag == "h2":
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading_text = tokens[i + 1].content

                    # 指定された見出しの場合、セクションを抽出
                    if heading_text in target_headings:
                        section_tokens = []
                        # 見出し自体を含める（h2開始、inline、h2終了）
                        section_tokens.extend([tokens[i], tokens[i + 1], tokens[i + 2]])

                        # 次の見出しまでのトークンを収集
                        j = i + 3
                        while j < len(tokens):
                            if tokens[j].type == "heading_open" and tokens[j].tag in [
                                "h1",
                                "h2",
                            ]:
                                break
                            section_tokens.append(tokens[j])
                            j += 1

                        # トークンをマークダウンに戻す
                        section_md = self._tokens_to_markdown(section_tokens)
                        sections.append(section_md)

                        i = j - 1

            i += 1

        return "\n\n".join(sections) if sections else ""

    def _tokens_to_markdown(self, tokens: list[Any]) -> str:
        """トークンをマークダウンテキストに変換"""
        result = []
        for token in tokens:
            if token.type == "heading_open":
                level = int(token.tag[1])
                result.append("#" * level + " ")
            elif token.type == "inline":
                result.append(token.content)
            elif token.type == "heading_close":
                result.append("\n\n")
            elif token.type == "paragraph_open":
                pass
            elif token.type == "paragraph_close":
                result.append("\n\n")
            elif token.type == "fence":
                result.append(f"```{token.info}\n{token.content}```\n\n")
            elif token.type == "bullet_list_open":
                pass
            elif token.type == "bullet_list_close":
                result.append("\n")
            elif token.type == "list_item_open":
                result.append("- ")
            elif token.type == "list_item_close":
                result.append("\n")
            elif hasattr(token, "content") and token.content:
                result.append(token.content)

        return "".join(result).strip()
