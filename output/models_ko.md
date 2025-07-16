# 모델 로딩[[loading-models]]

Transformers는 한 줄의 코드로 사용할 수 있는 많은 사전훈련된 모델을 제공합니다. 이를 위해서는 모델 클래스와 [`~PreTrainedModel.from_pretrained`] 메소드가 필요합니다.

[`~PreTrainedModel.from_pretrained`]를 호출하여 Hugging Face [Hub](https://hf.co/models)에 저장된 모델의 가중치와 구성을 다운로드하고 로드하세요.

> [!TIP]
> [`~PreTrainedModel.from_pretrained`] 메소드는 가능할 경우 [safetensors](https://hf.co/docs/safetensors/index) 파일 형식으로 저장된 가중치를 로드합니다. 전통적으로, PyTorch 모델 가중치는 보안에 취약한 것으로 알려진 [pickle](https://docs.python.org/3/library/pickle.html) 유틸리티로 직렬화됩니다. Safetensor 파일은 더 안전하고 로드 속도가 빠릅니다.

```py
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype="auto", device_map="auto")
```

이 가이드는 모델이 어떻게 로드되는지, 모델을 로드하는 다양한 방법, 정말 큰 모델에 대한 메모리 문제를 극복하는 방법, 사용자 정의 모델을 로드하는 방법을 설명합니다.
## 모델과 구성[[models-and-configurations]]

모든 모델에는 은닉 층의 수, 어휘 크기, 활성화 함수 등과 같은 특정 속성을 가진 `configuration.py` 파일이 있습니다. 또한 각 층 내부에서 발생하는 층과 수학적 연산을 정의하는 `modeling.py` 파일도 있습니다. `modeling.py` 파일은 `configuration.py`의 모델 속성을 가져와 모델을 그에 맞게 구축합니다. 이 시점에서, 의미 있는 결과를 출력하기 위해 훈련이 필요한 임의의 가중치를 가진 모델을 갖게 됩니다.

<!-- 모델과 구성의 다이어그램 삽입 -->

> [!TIP]
> *아키텍처*는 모델의 골격을 의미하고, *체크포인트*는 주어진 아키텍처에 대한 모델의 가중치를 의미합니다. 예를 들어, [BERT](./model_doc/bert)는 아키텍처이고 [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased)는 체크포인트입니다. *모델*이라는 용어는 아키텍처와 체크포인트와 상호 교환적으로 사용됩니다.

로드할 수 있는 모델에는 두 가지 일반적인 유형이 있습니다:

1. 은닉 상태를 출력하는 [`AutoModel`] 또는 [`LlamaModel`]과 같은 기본 모델.
2. 특정 작업을 수행하기 위해 특정 *헤드*가 부착된 [`AutoModelForCausalLM`] 또는 [`LlamaForCausalLM`]과 같은 모델.

각 모델 유형에 대해, 각 기계학습 프레임워크(PyTorch, TensorFlow, Flax)에 대한 별도의 클래스가 있습니다. 사용 중인 프레임워크에 맞는 접두사를 선택하세요.

<hfoptions id="backend">
<hfoption id="PyTorch">

```py
from transformers import AutoModelForCausalLM, MistralForCausalLM

# AutoClass 또는 모델별 클래스로 로드
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype="auto", device_map="auto")
model = MistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", torch_dtype="auto", device_map="auto")
```

</hfoption>
<hfoption id="TensorFlow">

```py
from transformers import TFAutoModelForCausalLM, TFMistralForCausalLM

# AutoClass 또는 모델별 클래스로 로드
model = TFAutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = TFMistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
```

</hfoption>
<hfoption id="Flax">

```py
from transformers import FlaxAutoModelForCausalLM, FlaxMistralForCausalLM

# AutoClass 또는 모델별 클래스로 로드
model = FlaxAutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = FlaxMistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
```

</hfoption>
</hfoptions>