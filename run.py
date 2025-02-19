from app import app
import keyboard

if __name__ == '__main__':
    app.run()

    # This doesn't work, obviously 
    while True: 
        if keyboard.read_key() == "n": 
            # print("Generate new BST") 
            app.run()