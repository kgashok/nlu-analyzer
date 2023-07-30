from app import app
import keyboard

if __name__ == '__main__':
    app.run()

    while True: 
        if keyboard.read_key() == "n": 
            print("Generate new BST") 
            app.run()