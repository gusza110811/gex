# test gex.py

import gex

if __name__ == "__main__":

    gex_instance = gex.UI(gex.Editor())
    test_commands = gex.deque([
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