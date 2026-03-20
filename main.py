from llama_cpp import Llama
from helpers.MessagesContainer import save_history
from Core.ReplyGenerator import chat_prompt_gen, system_promp_gen
from Core.CMND_Handler import Command_Executer, error_handler
from helpers.MessagesContainer import HISTORY_CONTAINER
from Tools.main import prompt_Analyzer
from helpers.Screen_Operation import get_current_screen
from TTS.main import TTSModel
from pathlib import Path

