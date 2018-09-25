import re
import logging
from cc_script.CcScriptPresenter import CcStringPresenter


class CcObject:
    class_tag_map = {}
    class_name= 'CcObject'
    asset_bundle = None

    def __init__(self, obj, parent_item=None):
        if isinstance(obj, CcObject):
            self.value_data = obj.value_data
        else:
            self.value_data = obj
        self.parent_item = parent_item

    def __repr__(self):
        return repr(self.value_data)

    def __str__(self):
        return self.value_string

    @classmethod
    def _get_class_type_by_data(cls, obj):
        if '__type__' in obj:
            tag = obj['__type__']
            return cls.class_tag_map[tag]
        if 'prefab' in obj and obj['prefab']:
            return cls.class_tag_map['cc.Prefab']
        return cls.class_tag_map['cc.Item']

    @classmethod
    def generate_tag_map(cls, symbols):
        for identifier, value in symbols.items():
            if isinstance(value, type(cls)) and value.__doc__:
                if value.__doc__.startswith('tag='):
                    tag = value.__doc__[4:]
                    cls.add_new_tag(tag, value)

    @classmethod
    def add_new_tag(cls, tag, class_type):
        cls.class_tag_map[tag] = class_type
        print(tag, '=', class_type)

    def get_object_from_data(self, class_type, data):
        if class_type is None or class_type is self.class_tag_map['cc.Item']:
            class_type = self._get_class_type_by_data(data)
        if issubclass(class_type, CcObject):
            return class_type(data, self)
        return class_type(data)

    def get_object_by_id(self, class_type, identifier):
        data = self.get_reference_by_id(identifier)
        if data is None:
            return None
        return self.get_object_from_data(class_type, data)

    def get_reference_by_id(self, identifier):
        if identifier not in self.value_data:
            # logging.warn(identifier + ' is not existing!')
            return None
        return self.value_data[identifier]

    def get_array_by_id(self, class_type, identifier):
        data = self.get_reference_by_id(identifier)
        if data is None:
            return []
        return_value = []
        for item in data:
            return_value.append(self.get_object_from_data(class_type, item))
        return return_value

    def post_init(self):
        pass

    @classmethod
    def bind(cls, item):
        return cls(item.value_data)

    def find_all(self):
        pass

    def write_header(self, presenter):
        pass

    def write_source(self, presenter):
        pass

    def write_value(self, presenter):
        pass

    @property
    def value_string(self):
        presenter = CcStringPresenter()
        self.write_value(presenter)
        return presenter.content

    @staticmethod
    def append(array, obj):
        assert isinstance(array, list)
        array.append(obj)

    @staticmethod
    def length(array):
        assert isinstance(array, list)
        return len(array)

    @staticmethod
    def qualified_name(name: str):
        assert isinstance(name, str)
        return re.sub(pattern='\W', repl='_', string=name)

    @staticmethod
    def make_string(obj):
        return str(obj)

    @classmethod
    def find_resource_by_uuid(cls, uuid):
        asset = cls.asset_bundle.get(uuid, None)
        if asset:
            return asset.path
        return None

    @classmethod
    def get_sub_metas(cls, meta):
        sub_metas = []
        class_type = cls.class_tag_map['cc.Meta']
        for k, v in meta.value_data['subMetas'].items():
            v['name'] = k
            sub_metas.append(class_type(v, meta))
        return sub_metas

    @classmethod
    def value_of(cls, value):
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)
