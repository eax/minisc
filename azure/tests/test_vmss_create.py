import unittest
from src.vmss_create import create_vmss

class TestVMSSCreate(unittest.TestCase):

    def test_create_vmss(self):
        # Assuming create_vmss returns a dictionary with a 'status' key
        result = create_vmss('test-resource-group', 'test-vmss', 'eastus', 2)
        self.assertEqual(result['status'], 'Succeeded')

if __name__ == '__main__':
    unittest.main()