import unittest
from taskpaper import TaskPaper, TaskItem


class EmptyObject(unittest.TestCase):
    def test_empty_taskpaper(self):
        "should handle empty object okay"
        til = TaskPaper()
        self.assertEqual(0, len(til.items))
        self.assertEqual(0, til.level())


class EmptyFile(unittest.TestCase):
    def test_missing_input(self):
        "Must pass input to parse"
        self.assertRaises(TypeError, TaskPaper.parse, (None,))

    def test_empty_input(self):
        "should handle empty file okay"
        til = TaskPaper.parse('')
        self.assertEqual(0, len(til.items))


class ParseItems(unittest.TestCase):
    def test_parse_project_no_tags(self):
        ti = TaskItem.parse('project:')
        self.assertTrue(ti.is_project())

    def test_parse_project_with_tags(self):
        # there are three formats for projects with tags, per TaskPaper v2.3.2
        # 1. colon at end
        # 2. colon before tags
        # 3. colon between tags
        valid_project_formats = [
            'project @tag:',
            'project: @tag',
            'project @tag: @tag2',
        ]
        for fmt in valid_project_formats:
            ti = TaskItem.parse(fmt)
            self.assertTrue(ti.is_project(), "did not accept '%s'" % (fmt,))

    def test_parse_task_no_tags(self):
        ti = TaskItem.parse('- task')
        self.assertTrue(ti.is_task())

    def test_parse_task_with_tags(self):
        ti = TaskItem.parse('- task @tag')
        self.assertTrue(ti.is_task())

    def test_parse_note_no_tags(self):
        ti = TaskItem.parse('note')
        self.assertTrue(ti.is_note())

    def test_parse_note_with_tags(self):
        ti = TaskItem.parse('note @tag')
        self.assertTrue(ti.is_note())


class ParseString(unittest.TestCase):
    def test_one_level(self):
        "Can't parse string, but doesn't error"
        input_string = 'project 1:\n\t- task 1\n\t- task 2\n'
        til = TaskPaper.parse(input_string)
        # will claim some large number of items
        self.assertTrue(len(til.items) > 3)

    def test_list_of_strings(self):
        lines = 'project 1:\n\t- task 1\n\t- task 2\n'.splitlines()
        til = TaskPaper.parse(lines)
        # one top level item
        self.assertEqual(1, len(til.items))
        # 3 total items
        self.assertEqual(3, sum(1 for _ in til))


class TagHandling(unittest.TestCase):
    lines = 'project 1 @tag1:\n\t- task 1 @tag1(content) @tag2(content)\n' \
            '\t- task 2 @tag2(multi word)\n' \
            '\t- task 3 @tag3(with \\) escaped @nested(tag\\))\n' \
            '\t- task 4 @tag4() empty args'.splitlines()

    def test_find_all_tags(self):
        "Find all tags"
        til = TaskPaper.parse(self.lines)
        tag_count = sum(len(list(i.tags.keys())) for i in til)
        self.assertEqual(6, tag_count)

    def test_find_desired_tags(self):
        "find just specified tags"
        til = TaskPaper.parse(self.lines)
        for tag in ('tag1', 'tag2'):
            tag_count = sum(1 for _ in til.select(lambda _: tag in _.tags))
            self.assertEqual(2, tag_count)

    def test_nested_escaped_tags(self):
        "proper parsing of escaped closing parens"
        til = TaskPaper.parse(self.lines)
        matches = list(til['tag3'])
        self.assertEqual(1, len(matches))
        self.assertEqual(matches[0].tags['tag3'], 'with \\) escaped @nested(tag\\)')

    def test_empty_args(self):
        "proper parsing of empty tag arguments"
        til = TaskPaper.parse(self.lines)
        matches = list(til['tag4'])
        self.assertEqual(1, len(matches))
        self.assertEqual(matches[0].txt, '- task 4 empty args')
        self.assertIs(matches[0].tags['tag4'], None)


class FormatCorrectness(unittest.TestCase):
    def test_format_no_tags(self):
        line = 'project 1:\n\t- task 1\n\tcomment 1'
        til = TaskPaper.parse(line.splitlines())
        output = til.format()
        self.assertEqual(line, output)

    def test_format_with_tags(self):
        # for projects, ending colon can be either before or after tags
        # so allow for either by reconverting
        line = 'project 1 @tag1:\n\t- task 1 @tag2\n\tcomment 1 @tag3'
        til_1 = TaskPaper.parse(line.splitlines())
        output_1 = til_1.format()
        til_2 = TaskPaper.parse(output_1.splitlines())
        output_2 = til_2.format()
        self.assertEqual(output_1, output_2)


if __name__ == '__main__':
    unittest.main()
