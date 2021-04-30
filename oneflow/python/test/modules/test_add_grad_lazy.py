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
from oneflow.python.nn.parameter import Parameter
import unittest
import numpy as np
from typing import Optional, Tuple


class Ones(flow.nn.Module):
    def __init__(self, dtype: Optional[flow.dtype] = None) -> None:
        super().__init__()
        if dtype == None or dtype == flow.int:
            dtype = flow.int
            floating_value = float(0)
            integer_value = int(1)
            is_floating_value = False
        else:
            dtype = flow.float
            floating_value = float(1)
            integer_value = int(0)
            is_floating_value = True

        self._op = (
            flow.builtin_op("constant")
            .Output("out")
            .Attr("floating_value", floating_value)
            .Attr("integer_value", integer_value)
            .Attr("is_floating_value", is_floating_value)
            .Attr("dtype", dtype)
        )

    def forward(self, shape):
        assert shape is not None, "shape should not be None!"
        assert isinstance(
            shape, (int, list, tuple)
        ), "shape should be int, list or tuple format!"
        if isinstance(shape, (int)):
            shape = [shape]
        self._op = self._op.Attr("shape", shape).Build()
        return self._op()[0]


class TestModule(flow.unittest.TestCase):
    def test_add_case1(test_case):
        flow.clear_default_session()
        init_val = np.random.randn(2, 3)

        def fn1():
            x = Parameter(flow.Tensor(init_val))

            y_ones = Ones(flow.float32)
            y = y_ones((2, 3))

            of_out = flow.add(x, y)

            of_out2 = flow.add(x, 4)
            return (of_out, of_out2)

        graph_fn = flow.compiler.trace(fn1, type="predict")

        of_out = graph_fn().get()
        test_case.assertTrue(
            np.allclose(of_out[0].numpy(), np.full((2, 3), init_val + 1), 1e-4, 1e-4)
        )
        test_case.assertTrue(
            np.allclose(of_out[1].numpy(), np.full((2, 3), init_val + 4), 1e-4, 1e-4)
        )

    def test_add_case2(test_case):
        flow.clear_default_session()
        init_val = np.random.randn(2, 3)

        def fn2():
            x = Parameter(flow.Tensor(init_val))

            y_ones = Ones(flow.float32)
            y = y_ones((2, 3))

            of_out = flow.add(x * 2.2, y)

            g_ones = Ones(flow.float32)
            grad = g_ones((2, 3))
            of_out.backward(grad)

            return x.grad

        graph_fn = flow.compiler.trace(fn2, type="predict")

        x_grad = graph_fn().get()
        test_case.assertTrue(
            np.allclose(x_grad.numpy(), np.full((2, 3), 2.2), 1e-4, 1e-4)
        )

    def test_add_case3(test_case):
        flow.clear_default_session()
        flow.config.enable_debug_mode(True)
        init_val = np.random.randn(2, 3)
        def fn3():
            x = Parameter(flow.Tensor(init_val))

            y_ones = Ones(flow.float32)
            y = y_ones((2, 3))

            of_out = flow.add(x*2, y)
            
            # lazy opt before backward
            g_ones = Ones(flow.float32)
            grad = g_ones((2, 3))
            of_out.backward(grad)

            param_list = list()
            param_list.append(x)
            sgd = flow.optim.SGD(param_list, lr=1.0, momentum=1.0)
            sgd.step()
            # sgd.zero_grad()
    
            return (of_out, x.grad, x)

        graph_fn = flow.compiler.trace(fn3)
        # graph_fn = flow.compiler.trace(fn3, type="predict")

        x_val = init_val
        x_grad_val = 0 
        for i in range(5):
            print("run {}th time:".format(i))
            out = graph_fn().get()
            print("loss ", out[0].numpy())
            x_grad_val = out[1].numpy()
            print("x.grad ", x_grad_val)
            print("x now should be", x_val)
            # here return x value before update
            print("x before update ", out[2].numpy())
            test_case.assertTrue(
                np.allclose(out[2].numpy(), x_val, 1e-4, 1e-4)
            )
            x_val -= x_grad_val


if __name__ == "__main__":
    unittest.main()
