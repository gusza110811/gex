# test gex.py

from gex import UI
from editor import Editor
from collections import deque

if __name__ == "__main__":

    gex_instance = UI(Editor())
    test_commands = deque([
        "i1;Hello, World!",
        "i2;This was line 2",
        "i.;inserted at line 2",
        ";Append mode test",
        ";",
        "multiline Append test",
        ".",
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
        print(f"{i+1}: {line}")