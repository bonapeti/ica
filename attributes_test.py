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

def test_mandatory_attribute():
    object_description = {
                            "attr1" : { "ignore_if_empty": False }
                        }
    class TestObject:
        attr1 = "value"
    assert { "attr1": "value" } == attributes.object_as_yaml(TestObject(), object_description)

def test_optional_attribute_but_existing():
    object_description = {
                            "attr1" : { "ignore_if_empty": True }
                        }
    class TestObject:
        attr1 = ""
    assert { } == attributes.object_as_yaml(TestObject(), object_description)
