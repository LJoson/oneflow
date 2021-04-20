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
import unittest
import numpy as np


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in eager mode",
)
class TestModule(flow.unittest.TestCase):
    def test_mul(test_case):
        x = flow.Tensor(np.random.randn(2, 3))
        y = flow.Tensor(np.random.randn(2, 3))
        of_out = flow.mul(x, y)
        np_out = np.multiply(x.numpy(), y.numpy())
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        x = 5
        y = flow.Tensor(np.random.randn(2, 3))
        of_out = flow.mul(x, y)
        np_out = np.multiply(x, y.numpy())
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        x = flow.Tensor(np.random.randn(2, 3))
        y = 5
        of_out = flow.mul(x, y)
        np_out = np.multiply(x.numpy(), y)
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        x = flow.Tensor(np.random.randn(1, 1))
        y = flow.Tensor(np.random.randn(2, 3))
        of_out = flow.mul(x, y)
        np_out = np.multiply(x.numpy(), y.numpy())
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        # test __mul__
        x = flow.Tensor(np.random.randn(1, 1))
        y = flow.Tensor(np.random.randn(2, 3))
        of_out = x * y
        np_out = np.multiply(x.numpy(), y.numpy())
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        x = flow.Tensor(np.random.randn(2, 3))
        of_out = x * 3
        np_out = np.multiply(x.numpy(), 3)
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

        x = flow.Tensor(np.random.randn(2, 3))
        of_out = 3 * x
        np_out = np.multiply(3, x.numpy())
        test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))

    
    def test_matmul(test_case):
        x = flow.Tensor(np.random.randn(2, 4))
        y = flow.Tensor(np.random.randn(4, 2))
        m = flow.nn.MatMul()

        np_out = np.matmul(x.numpy(), y.numpy())
        print("np_out >>>>>>>>>>>>>>> \n", np_out)

        of_out = m(x, y)
        print("of_out >>>>>>>>>>>>>>> \n", of_out.numpy())

        # test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-4, 1e-4))



if __name__ == "__main__":
    unittest.main()
