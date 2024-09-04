import torch

from invokeai.backend.flux.model import Flux
from invokeai.backend.flux.util import params
from invokeai.backend.lora.conversions.flux_lora_conversion_utils import convert_flux_kohya_state_dict_to_invoke_format
from tests.backend.lora.conversions.lora_state_dicts.flux_lora_kohya_format import state_dict_keys


def test_convert_flux_kohya_state_dict_to_invoke_format():
    # Construct state_dict from state_dict_keys.
    state_dict: dict[str, torch.Tensor] = {}
    for k in state_dict_keys:
        state_dict[k] = torch.empty(1)

    converted_state_dict = convert_flux_kohya_state_dict_to_invoke_format(state_dict)

    # Extract the prefixes from the converted state dict (i.e. without the .lora_up.weight, .lora_down.weight, and
    # .alpha suffixes).
    converted_key_prefixes: list[str] = []
    for k in converted_state_dict.keys():
        k = k.replace(".lora_up.weight", "")
        k = k.replace(".lora_down.weight", "")
        k = k.replace(".alpha", "")
        converted_key_prefixes.append(k)

    # Initialize a FLUX model on the meta device.
    with torch.device("meta"):
        model = Flux(params["flux-dev"])
    model_keys = set(model.state_dict().keys())

    # Assert that the converted state dict matches the keys in the actual model.
    for converted_key_prefix in converted_key_prefixes:
        found_match = False
        for model_key in model_keys:
            if model_key.startswith(converted_key_prefix):
                found_match = True
                break
        if not found_match:
            raise AssertionError(f"Could not find a match for the converted key prefix: {converted_key_prefix}")