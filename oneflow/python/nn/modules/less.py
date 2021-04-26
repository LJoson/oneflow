"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import oneflow as flow
from oneflow.python.nn.module import Module
from oneflow.python.oneflow_export import oneflow_export
from oneflow.python.framework.tensor import register_tensor_op_by_module
from oneflow.python.framework.tensor import register_op_by_module


@oneflow_export("Less")
@register_op_by_module("lt")
class Less(Module):
    r"""Returns the truth value of :math:`x < y` element-wise.

    Args:
        x (oneflow.Tensor): A Tensor
        y (oneflow.Tensor): A Tensor
        name (Optional[str], optional): The name for the operation. Defaults to None.

    Returns:
        oneflow.Tensor: A Tensor with int8 type.

    For example:

    .. code-block:: python

        import oneflow as flow
        import numpy as np
        
        input1 = flow.Tensor(np.array([1, 2, 3]).astype(np.float32), dtype=flow.float32)
        input2 = flow.Tensor(np.array([1, 2, 4]).astype(np.float32), dtype=flow.float32)
        
        out = flow.gt(input1, input2).numpy

        # out [0 0 1]

    """

    def __init__(self) -> None:
        super().__init__()
        self._op = (
            flow.builtin_op("broadcast_less").Input("x").Input("y").Output("z").Build()
        )

    def forward(self, x, y):
        return self._op(x, y)[0]


@register_tensor_op_by_module("lt")
def less_op(tensor1, tensor2):
    return Less()(tensor1, tensor2)