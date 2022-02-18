# NotionImportEBook

import github ebooks (markdown files) to notions.

将github中的 `*.md` 的电子书导入到 __notion__ 中.

Developing...

开发中...

# TODO

- [ ] blocks
  - [x] code
  - [x] p
  - [x] ul
  - [x] ol
  - [x] headers(h1\h2\h3...)
  - [ ] rich-text
  - [x] picture
- [ ] add logger
- [ ] add sqlite to store notion-db __ ebook map relation, for update
- [ ] refactor block class
- [x] pic management (oss)
- [ ] page version control
- [ ] toc
- [ ] more properties (unread, pinned, ...)

## Question

- list block not support nested.
  use queue?
- how to handle page version?
  use page properties?