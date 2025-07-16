# Loading models

Transformers provides many pretrained models that are ready to use with a single line of code. It requires a model class and the [`~PreTrainedModel.from_pretrained`] method.

Call [`~PreTrainedModel.from_pretrained`] to download and load a model's weights and configuration stored on the Hugging Face [Hub](https://hf.co/models).

> [!TIP]
> The [`~PreTrainedModel.from_pretrained`] method loads weights stored in the [safetensors](https://hf.co/docs/safetensors/index) file format if they're available. Traditionally, PyTorch model weights are serialized with the [pickle](https://docs.python.org/3/library/pickle.html) utility which is known to be unsecure. Safetensor files are more secure and faster to load.

```py
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype="auto", device_map="auto")
```

This guide explains how models are loaded, the different ways you can load a model, how to overcome memory issues for really big models, and how to load custom models.

## Models and configurations

All models have a `configuration.py` file with specific attributes like the number of hidden layers, vocabulary size, activation function, and more. You'll also find a `modeling.py` file that defines the layers and mathematical operations taking place inside each layer. The `modeling.py` file takes the model attributes in `configuration.py` and builds the model accordingly. At this point, you have a model with random weights that needs to be trained to output meaningful results.

<!-- insert diagram of model and configuration -->

> [!TIP]
> An *architecture* refers to the model's skeleton and a *checkpoint* refers to the model's weights for a given architecture. For example, [BERT](./model_doc/bert) is an architecture while [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased) is a checkpoint. You'll see the term *model* used interchangeably with architecture and checkpoint.

There are two general types of models you can load:

1. A barebones model, like [`AutoModel`] or [`LlamaModel`], that outputs hidden states.
2. A model with a specific *head* attached, like [`AutoModelForCausalLM`] or [`LlamaForCausalLM`], for performing specific tasks.

For each model type, there is a separate class for each machine learning framework (PyTorch, TensorFlow, Flax). Pick the corresponding prefix for the framework you're using.

<hfoptions id="backend">
<hfoption id="PyTorch">

```py
from transformers import AutoModelForCausalLM, MistralForCausalLM

# load with AutoClass or model-specific class
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype="auto", device_map="auto")
model = MistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype="auto", device_map="auto")
```

</hfoption>
<hfoption id="TensorFlow">

```py
from transformers import TFAutoModelForCausalLM, TFMistralForCausalLM

# load with AutoClass or model-specific class
model = TFAutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = TFMistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
```

</hfoption>
<hfoption id="Flax">

```py
from transformers import FlaxAutoModelForCausalLM, FlaxMistralForCausalLM

# load with AutoClass or model-specific class
model = FlaxAutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = FlaxMistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
```

</hfoption>
</hfoptions>
