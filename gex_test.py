# test gex.py

from gex import UI
from editor import Editor
from collections import deque

if __name__ == "__main__":

    gex_instance = UI(Editor())
    test_commands = deque([
        "+1;Hello, World!",".",
        "+2;This is line 2.",".",
        "+.;Modified line 1.",".",
        "s",
        "q", "y"
    ])

    def mock_input(prompt):
        if test_commands:
            cmd = test_commands.popleft()
            print(f"{prompt}{cmd}")
            return cmd
        else:
            raise EOFError("No more test commands.")

    gex_instance.input = mock_input
    
    gex_instance.main()

    print("\nFinal buffer state:")
    for i, line in enumerate(gex_instance.editor.getLines()):
        print(f"{i}: {line}")