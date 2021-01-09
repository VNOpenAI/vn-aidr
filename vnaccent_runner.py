import os
import json
import argparse

import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from model_utils.vn_accent.accent_utils import extract_words, remove_tone_line
from model_utils.vn_accent.models.transformer_utils.mask import create_src_mask
from model_utils.vn_accent.models.model_factory import get_model
from config import *

class VNAccentRunner():

    def __init__(self):
        # Load tokenizer
        print("Load tokenizer")
        tokenizer = torch.load(ACCENT_MODEL_TOKENIZER_PATH)
        self.src_tokenizer = tokenizer['notone']
        self.trg_tokenizer = tokenizer['tone']
        src_pad_token = 0
        trg_pad_token = 0

        # Load model
        print("Init model")
        with open(ACCENT_MODEL_CONFIG_PATH) as f:
            config = json.load(f)
        
        if ACCENT_MODEL_NAME in config:
            self.model_param = config[ACCENT_MODEL_NAME]
        else:
            raise Exception("Invalid model name")
        
        self.model_param['src_vocab_size'] = len(self.src_tokenizer.word_index) + 1
        self.model_param['trg_vocab_size'] = len(self.trg_tokenizer.word_index) + 1

        self.model = get_model(self.model_param)
        self.device = torch.device('cuda' if torch.cuda.is_available() and USE_GPU else 'cpu')
        print("Using", self.device.type)
        if self.device.type=='cuda':
            self.model = model.cuda()

        if os.path.isfile(ACCENT_MODEL_PATH):
            print("Load model")
            state = torch.load(ACCENT_MODEL_PATH)
            if isinstance(state, dict):
                self.model.load_state_dict(state['model'])
            else:
                self.model.load_state_dict(state)
        else:
            raise Exception("Invalid weight path")

    
    def predict(self, text):
        """
        Input: No-tone sentence
        Output: Accent-added sentence
        """
        res = VNAccentRunner.translate(self.model, text, self.src_tokenizer, self.trg_tokenizer, use_mask=self.model_param["use_mask"], device=self.device)
        return res


    @staticmethod
    def translate(model, sents, src_tokenizer, trg_tokenizer, maxlen=200, use_mask=True, device=None):
        
        words, word_indices = extract_words(sents)
        lower_words = [x.lower() for x in words]

        # Tokenize words
        known_word_mask = [] # Same size as words - True if word is in word list, otherwise False
        seqs = []
        for word in lower_words:
            if word in src_tokenizer.word_index:
                seqs.append(src_tokenizer.word_index[word])
                known_word_mask.append(True)
            else:
                seqs.append(1)
                known_word_mask.append(False)
        seqs = [seqs]

        # Model inference
        seqs = pad_sequences(seqs, maxlen, padding='post')
        seqs = torch.tensor(seqs).long()
        if device is not None and device.type=='cuda':
            seqs = seqs.cuda()
        with torch.no_grad():
            probs = forward(model, seqs, 0, use_mask=use_mask)
        probs = probs.cpu().detach().numpy()
        
        # Add tone
        output = sents
        probs = probs[0]
        prob_indices = probs.argsort(axis=-1)[:, ::-1]
        prob_indices = prob_indices[:, :100]
        for i, word in enumerate(lower_words):
            
            # Skip unknown words
            if not known_word_mask[i]:
                continue

            # Find the best solution
            for idx in prob_indices[i, :]:
                target_word = trg_tokenizer.sequences_to_texts([[idx]])[0]
                if remove_tone_line(target_word.lower()) == word:
                    begin_idx, end_idx = word_indices[i]

                    # Correct lower / upper case
                    corrected_word = ""
                    for ic, char in enumerate(words[i]):
                        if char.islower():
                            corrected_word += target_word[ic].lower()
                        else:
                            corrected_word += target_word[ic].upper()

                    output = output[:begin_idx] + corrected_word + output[end_idx:]
                    break

        return output

