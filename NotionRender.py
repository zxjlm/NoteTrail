import os
import pathlib
from pprint import pprint

import re
import sys
from itertools import chain
from urllib.parse import quote
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
from mistletoe.base_renderer import BaseRenderer

from OSSHandler import oss_handler
from utils import markdown_render, erase_prefix_string

if sys.version_info < (3, 4):
    from mistletoe import _html as html
else:
    import html


class NotionRender(BaseRenderer):
    """
    HTML renderer class.

    See mistletoe.base_renderer module for more info.
    """

    def __init__(self, mdfile_path, basic_path, bookname, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self._suppress_ptag_stack = [False]
        self._up_level = [False]
        super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(r'&(#[0-9]+;'
                              r'|#[xX][0-9a-fA-F]+;'
                              r'|[^\t\n\f <&#;]{1,32};)')
        html._charref = _charref

        self.mdfile_path = mdfile_path
        self.basic_path = basic_path
        self.bookname = bookname

    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return self.escape_html(token.content)

    def render_strong(self, token):
        rich_text_template = {
            "type": "text",
            "text": {
                "content": ''.join(
                    [child.content for child in token.children if child.__class__.__name__ == 'RawText']),
                "link": None,
            },
            "annotations": {
                "bold": True
            },
        }
        return rich_text_template

    def render_emphasis(self, token):
        template = '<em>{}</em>'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = '<code>{}</code>'
        inner = html.escape(token.children[0].content)
        return template.format(inner)

    def render_strikethrough(self, token):
        template = '<del>{}</del>'
        return template.format(self.render_inner(token))

    def render_image(self, token):
        img_path = os.path.join(os.path.dirname(self.mdfile_path), token.src)
        img_path = pathlib.Path(img_path).__str__()
        storage_path = os.path.join(self.bookname, erase_prefix_string(img_path, self.basic_path))
        oss_url = oss_handler.upload_pic(img_path, storage_path)
        block_template = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": oss_url
                }
            }
        }
        return block_template

    def render_link(self, token):
        # template = '<a href="{target}"{title}>{inner}</a>'
        # target = self.escape_url(token.target)
        # if token.title:
        #     title = ' title="{}"'.format(self.escape_html(token.title))
        # else:
        #     title = ''
        # inner = self.render_inner(token)
        # return template.format(target=target, title=title, inner=inner)
        rich_text_template = {
            "type": "text",
            "text": {
                "content": ''.join(
                    [child.content for child in token.children if child.__class__.__name__ == 'RawText']),
                "link": None,
            },
            "href": token.target,
        }
        return rich_text_template

    def render_auto_link(self, token):
        template = '<a href="{target}">{inner}</a>'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token):
        return {
            "type": "text",
            "text": {
                "content": token.content,
                "link": None,
            }
        }

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        inner = self.render_inner(token)
        head_leval = "heading_{}".format(token.level if token.level <= 3 else 3)
        block_template = {
            "type": head_leval,
            head_leval: {
                "text": inner
            }
        }
        return block_template

    def render_quote(self, token):
        elements = ['<blockquote>']
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]:
            return self.render_inner(token)
        if token.children.__len__() == 1 and token.children[0].__class__.__name__ == 'Image':
            return self.render_inner(token)[0]
        inner = self.render_inner(token)
        block_template = {
            "type": "paragraph",
            "paragraph": {
                "text": inner,
            }
        }
        return block_template

    def render_block_code(self, token):
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        block_template = {
            "type": "paragraph",
            "paragraph": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": "",
                        "link": None
                    }
                }],
                "children": []
            }
        }
        self._suppress_ptag_stack.append(not token.loose)
        inner = [self.render(child) for child in token.children]
        block_template[block_template['type']]['children'] = inner
        self._suppress_ptag_stack.pop()
        return block_template

    def render_list_item(self, token):
        if token.leader == '-':
            block_template = {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "text": [],
                    "children": []
                }
            }
        else:
            block_template = {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "text": [],
                    "children": []
                }
            }

        if len(token.children) == 0:
            return block_template
        inner = [self.render(child) for child in token.children]
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == 'Paragraph':
                block_template[block_template['type']]['children'] = inner[1:]
                block_template[block_template['type']]['text'] = inner[0]
            if token.children[-1].__class__.__name__ == 'Paragraph':
                block_template[block_template['type']]['children'] = inner[:-1]
                block_template[block_template['type']]['text'] = inner[-1]
        else:
            block_template[block_template['type']]['children'] = inner
        # block_template[block_template['type']]['children'] = inner
        return block_template

    def render_table(self, token):
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered + body_rendered)

    def render_table_row(self, token, is_header=False):
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
        template = '<{tag}{attr}>{inner}</{tag}>\n'
        tag = 'th' if in_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, attr=attr, inner=inner)

    @staticmethod
    def render_thematic_break(token):
        return {
            "type": "divider",
            "divider": {}
        }

    @staticmethod
    def render_line_break(token):
        return {
            "type": "text",
            "text": {
                "content": "",
                "link": None
            }
        }

    @staticmethod
    def render_html_block(token):
        return token.content

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        # inner = '\n'.join([self.render(child) for child in token.children])
        # return '{}\n'.format(inner) if inner else ''
        return [self.render(child) for child in token.children]

    @staticmethod
    def escape_html(raw):
        return html.escape(html.unescape(raw)).replace('&#x27;', "'")

    @staticmethod
    def escape_url(raw):
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&;'))

    def render_inner(self, token):
        # if token.__class__.__name__ == 'List':
        #     return map(self.render, token.children)
        try:
            return ''.join(map(self.render, token.children))
        except Exception as _e:
            return list(map(self.render, token.children))

    def render_multi_objects_and_combine(self, tokens):
        pass

    # def split_children(self, token):
    #     """
    #     split children to text and non-text group
    #     :return:
    #     """
    #     text, non_text = [], []
    #     for child in token.children:
    #         if child.__class__.__name__ == 'RawText':


if __name__ == "__main__":
    # body.children[82].paragraph.text[1].text
    md_path_ = '/home/harumonia/projects/docs/note-book2-master/docs/ddd/03/06.md'
    with open(md_path_) as f:
        node = markdown_render(f.readlines(), md_path_, "/home/harumonia/projects/docs/note-book2-master/docs/ddd/",
                               'ddd', NotionRender)
        pprint(node)
