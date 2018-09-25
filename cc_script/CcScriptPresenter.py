class CcScriptPresenter:
    def __init__(self, target_file, tab_space='\t'):
        self.file = target_file
        self.tab_space = tab_space
        self.indent = 0
        self.follow_if = False

    def shift_indent(self, shift=True):
        if shift:
            self.indent += 1
        else:
            assert self.indent > 0
            self.indent -= 1

    def write_line(self, *lines):
        self.write_tabs()
        for line in lines:
            self.write(line)
        self._write_endl()

    def write_tabs(self):
        self.file.write(self.tab_space * self.indent)

    def _write_endl(self):
        self.file.write('\n')

    def write_crlf(self, tag, count=1):
        crlf = '\n' * count
        # self.file.write(f'<crlf {tag}:{count}>\n')
        self.file.write(f'{crlf}')

    def write(self, string):
        self.file.write(string)

    @property
    def content(self):
        return None


class CcStringPresenter(CcScriptPresenter):
    def __init__(self, tab_space='\t'):
        super().__init__(target_file=None, tab_space=tab_space)
        self._content = []

    def shift_indent(self, shift=True):
        pass

    def write_line(self, *lines):
        self.write_tabs()
        for line in lines:
            self.write(line)
        self._write_endl()

    def write_tabs(self):
        pass

    def _write_endl(self):
        pass

    def write_crlf(self, tag, count=1):
        pass

    def write(self, string):
        self._content.append(string)

    @property
    def content(self):
        return ''.join(self._content)
