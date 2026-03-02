import os
import sys
import unittest

# ensure project root is on sys.path when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import Quiz

# QuizView requires discord, which might not be installed in the test
# environment.  If the import fails we skip the related tests.
try:
    from utils import QuizView
    import discord
except ImportError:  # either discord or QuizView missing
    QuizView = None


class QuizTests(unittest.TestCase):
    def test_quiz_fields(self):
        q = Quiz()
        self.assertIsInstance(q.question_content, str)
        self.assertEqual(len(q.answer), 4)

    @unittest.skipIf(QuizView is None, "discord package not available")
    def test_view_builds_buttons(self):
        q = Quiz()
        view = QuizView(q, author=None)
        # there should be exactly four button children
        buttons = [c for c in view.children if isinstance(c, discord.ui.Button)]
        self.assertEqual(len(buttons), 4)
        self.assertEqual([b.label for b in buttons], q.answer)


if __name__ == "__main__":
    unittest.main()
