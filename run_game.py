import sys
from PyQt5.QtWidgets import QApplication
from game.game_gui import GameGUI

app = QApplication([])
game = GameGUI()
sys.exit(app.exec_())