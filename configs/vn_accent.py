import json

class VNAccentConfig:

    ACCENT_MODEL_CONFIG_PATH = "model_utils/vn_accent/model_config.json"
    CONFIGS = {
        "transformer_evolved": {
            "model_type": "transformer_evolved",
            "tokenizer_path": "trained_models/vn_accent/tokenizer.h5",
            "weights": "trained_models/vn_accent/transformer_evolved_ep14.h5"
        }
    }

    def __init__(self, model_name="transformer_evolved"):

        with open(VNAccentConfig.ACCENT_MODEL_CONFIG_PATH) as f:
            config = json.load(f)

        if model_name in config:
            self.model_param = config[VNAccentConfig.CONFIGS[model_name]["model_type"]]
        else:
            raise Exception("Invalid model name")

        self.tokenizer_path = VNAccentConfig.CONFIGS[model_name]["tokenizer_path"]
        self.weights = VNAccentConfig.CONFIGS[model_name]["weights"]
    