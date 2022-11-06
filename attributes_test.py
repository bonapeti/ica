import attributes
import pytest

def test_basic_definition():
    object_description = {
                            "attr1" : { }
                        }
    class TestObject:
        attr1 = "value"
    assert { "attr1": "value" } == attributes.object_as_yaml(TestObject(), object_description)

def test_basic_definition_with_missing_attribute():
    object_description = {
                            "missing_attribute" : { }
                        }
    class TestObject:
        attr1 = "value"

    with pytest.raises(AttributeError):
        attributes.object_as_yaml(TestObject(), object_description)
