from cc_grammar import CcScriptParser
from cc_script.CcScriptPresenter import *
from cc_model.CcModelBase import CcObject
import json
import sys
import os

if len(sys.argv) > 2 and sys.argv[2] == '--load-script':
    script = CcScriptParser.parse(script_path='./Data/ccreator.cpp')
    if not script:
        raise Exception('parse failed!')
else:
    script = None
from cc_model.CcModel import *


class CcAssetsBundle:
    def __init__(self, path):
        self.script = script
        self.assets = {}
        self.sprite_files = []
        self.animation_files = []
        self.fire_files = []
        self.root_path = path

    def __repr__(self):
        return 'Bundle:' + repr(self.assets)

    def __str__(self):
        return 'Bundle:' + str(self.assets)

    def _process_file(self, path):
        if path.endswith('.fire'):
            self.fire_files.append(os.path.relpath(path, self.root_path))
        elif path.endswith('.anim'):
            self.animation_files.append(os.path.relpath(path, self.root_path))
        elif path.endswith('.png'):
            self.sprite_files.append(os.path.relpath(path, self.root_path))

    def _process_dir(self, path):
        for f in os.listdir(path):
            real_path = os.path.join(path, f)
            if os.path.isdir(real_path):
                self._process_dir(real_path)
            elif os.path.isfile(real_path):
                self._process_file(real_path)

    def load(self):
        for rel_path in ('assets', 'temp/internal'):
            self._process_dir(os.path.join(self.root_path, rel_path))
        for path in self.sprite_files:
            self._load_sprite(path)
        for path in self.animation_files:
            self._load_animclip(path)
        for path in self.fire_files:
            self._load_scene(path)

    def _load_sprite(self, path):
        obj = CcAssetSprite(bundle=self, path=path)
        self.assets[obj.uuid] = obj

    def _load_animclip(self, path):
        obj = CcAssetAnimationClip(bundle=self, path=path)
        self.assets[obj.uuid] = obj

    def _load_scene(self, path):
        obj = CcAssetScene(bundle=self, path=path)
        self.assets[obj.uuid] = obj


class CcAssetResource:
    def __init__(self, bundle: CcAssetsBundle, path: str):
        self.bundle = bundle
        self.name, _ = os.path.splitext(os.path.basename(path))
        self.meta = CcAssetMeta(bundle, path + '.meta')
        self.uuid = self.meta.uuid
        self.value = self.load(path=path)
        self.path = path
        print(f'resource=\"{self.name}\" {self.path} \"{self.uuid}\"')

    def __repr__(self):
        return repr(self.value)

    def load(self, path):
        pass


class CcAssetMeta:
    def __init__(self, bundle: CcAssetsBundle, path: str):
        self.bundle = bundle
        self.path = path
        self.value = self.load(path=path)

    def load(self, path):
        json_file = open(os.path.join(self.bundle.root_path, path), 'r')
        root = json.load(fp=json_file)
        return Meta(root, None)

    @property
    def uuid(self):
        return self.value.get_uuid()


class CcAssetSprite(CcAssetResource):
    def __init__(self, bundle: CcAssetsBundle, path: str):
        super().__init__(bundle=bundle, path=path)


class CcAssetAnimationClip(CcAssetResource):
    def __init__(self, bundle: CcAssetsBundle, path: str):
        super().__init__(bundle=bundle, path=path)

    def load(self, path):
        json_file = open(os.path.join(self.bundle.root_path, path), 'r')
        root = json.load(fp=json_file)
        return AnimationClip(root, None)


class CcAssetScene(CcAssetResource):
    def __init__(self, bundle: CcAssetsBundle, path: str):
        super().__init__(bundle=bundle, path=path)
        assert self.uuid == self.value.get_uuid()

    def load(self, path):
        json_file = open(os.path.join(self.bundle.root_path, path), 'r')
        root = {'name': self.qualified_name, 'items': json.load(fp=json_file)}
        return Fire(root, None)

    @property
    def qualified_name(self):
        return self.name


if __name__ == '__main__':
    _bundle = CcAssetsBundle(sys.argv[1])
    _bundle.load()
    CcObject.asset_bundle = _bundle.assets
    for resource in _bundle.assets.values():
        if isinstance(resource, CcAssetScene):
            header_file = open(f'Output/{resource.name}.h', 'w')
            resource.value.write_header(presenter=CcScriptPresenter(header_file))
            source_file = open(f'Output/{resource.name}.cpp', 'w')
            resource.value.write_source(presenter=CcScriptPresenter(source_file))
