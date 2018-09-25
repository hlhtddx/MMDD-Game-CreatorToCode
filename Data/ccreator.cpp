class Project {
    string engine;
    string packages;
}

class Id {
    int __id__;
    void write_value() {
        = __id__;
    }
}

class Uuid {
    string __uuid__;
    void write_value() {
        = __uuid__;
    }
}

class Vec2
{
    float x;
    float y;
    void write_value() {
        = "Vec2(", x, ", ", y, ")";
    }
}

class Vec3
{
    float x;
    float y;
    float z;
    void write_value() {
        = "Vec3(", x, ", ", y, ", ", z, ")";
    }
}

class Size
{
    float width;
    float height;
    void write_value() {
        = "Size(", width, ", ", height, ")";
    }
}

class Rect
{
    float x;
    float y;
    float w;
    float h;
    void write_value() {
        = "Rect(", x, ", ", y, ", ", w, ", ", h, ")";
    }
}

class Color3B
{
    ubyte r;
    ubyte g;
    ubyte b;
    void write_value() {
        = "Color3B(", r, ", ", g, ", ", b, ")";
    }
}

class Color4B
{
    ubyte r;
    ubyte g;
    ubyte b;
    ubyte a;
    void write_value() {
        = "Color4B(", r, ", ", g, ", ", b, ", ", a, ")";
    }
}

class Item : "cc.Item" {
    string __type__;
	string name : "_name";
    Id node;
    Id parent : "_parent";
    Id@ children : "_children";
    Id@ components : "_components";
    void __ctor__() {
        Root = parent_item;
    }

    void post_init() {
        Parent = Root.find(parent);
        if (!Parent) Parent = Root.find(node);
        Children = Root.find_all_items(children);
        Components = Root.find_all_items(components);
        if(name) Name = qualified_name(name);
        else Name = "node_" + make_string(id);
    }

    void get_component(string __type__) {
        for component in Components {
            if (component.__type__ == __type__) {
                return component;
            }
        }
        return null;
    }

    void write_header() {
        = {
            Children, Components;
        }
    }

    void write_setup_scene() {
        = "/* Item=", id, ", name=", Name, ", type=", __type__, " */";

        > {
            "/* Start Components=", id, ", name=", Name, ", type=", __type__, " */";
            $ for component in Components {
                component.write_setup_scene();
            }
            "/* End Components=", id, ", name=", Name, ", type=", __type__, " */";
        }

        > {
            "/* Start Children=", id, ", name=", Name, ", type=", __type__, " */";
            $ for child in Children {
                child.write_setup_scene();
            }
            "/* End Children=", id, ", name=", Name, ", type=", __type__, " */";
        }
    }

    void write_create_scene() {
        = "/* Item=", id, ", name=", Name, " */";
        for component in Components {
            component.write_create_scene();
        }
        for child in Children {
            $ child.write_create_scene();
        }
    }

    void write_property(string nodeName) {
        ;
    }

internal:
    Fire Root;
    string Name;
    Item Parent;
    Item@ Children;
    Item@ Components;
    int id;
}

class Node : "cc.Node" extends Item {
	Size contentSize : "_contentSize";
	bool active : "_active";
	bool enabled : "_enabled";
	Vec2 anchorPoint : "_anchorPoint";
	bool cascadeOpacityEnabled : "_cascadeOpacityEnabled";
	Color3B color : "_color";
	int globalZOrder : "_globalZOrder";
	int localZOrder : "_localZOrder";
	int opacity : "_opacity";
	bool opacityModifyColor3B : "_opacityModifyColor3B";
	Vec2 position : "_position";
	int rotationSkewX : "_rotationX";
	int rotationSkewY : "_rotationY";
	float scaleX : "_scaleX";
	float scaleY : "_scaleY";
	int skewX : "_skewX";
	int skewY : "_skewY";
	int tag : "_tag";
	int groupIndex : "groupIndex";
    int objFlags : "_objFlags" = 0;
    string rawFiles : "_rawFiles";
    string visible;

    void write_setup_scene() {
        = "/* Node=", id, ", name=", Name, ", type=", __type__, " */";
        super.write_setup_scene();
    }

    void write_create_scene() {
        = "/* Node=", id, ", name=", Name, ", type=", __type__, " */";
        super.write_create_scene();
    }

    void write_property(string nodeName) {
        = {
        nodeName.globalZOrder = globalZOrder;
        nodeName.localZOrder = localZOrder;
        string nodeNameStr = "\"" + nodeName + "\"";
        nodeName.name = nodeNameStr;
        nodeName.anchorPoint = anchorPoint;
        nodeName.color = color;
        nodeName.opacity = opacity;
        nodeName.opacityModifyColor3B = opacityModifyColor3B;
        nodeName.position = position;
        nodeName.rotationSkewX = rotationSkewX;
        nodeName.rotationSkewY = rotationSkewY;
        nodeName.scaleX = scaleX;
        nodeName.scaleY = scaleY;
        nodeName.skewX = skewX;
        nodeName.skewY = skewY;
        nodeName.tag = tag;
        nodeName.contentSize = contentSize;
        nodeName.visible = enabled;
        }
    }
}

class Fire {
    string name;
    Item@ items;
internal:
    string _uuid;

    void __ctor__() {
        Scene scene = items[1];
        scene.name = qualified_name(name);
        _uuid = scene.id;
        int i = 0;
        for item in items {
            item.id = i;
            item.post_init();
            i = i + 1;
        }
    }

    string get_uuid() {
        return _uuid;
    }

    void write_header() {
        = {
        "#include \"cocos2d.h\"";
        "#include \"ui/CocosGUI.h\"";
        ;
        "USING_NS_CC;";
        ;
        "class " + qualified_name(name) + " : public Node {";
        > {
            "public:";
            "// create scene";
            "void setupScene();";
            "static cocos2d::Scene* createScene();";
            ;
        }
        "};";
        ;
        }
    }

    void write_source() {
        = {
        "#include \"" + name + ".h\"";
        ;
        }
        SceneAsset asset = items[0];
        asset.write_source();
    }

    Item find(Id pid) {
    if(pid)
        return items[pid.__id__];
    }

    Item@ find_all_items(Id@ item_ids) {
        Item@ sub_items;
        for item_id in item_ids {
            sub_items.append(items[item_id.__id__]);
        }
        return sub_items;
    }
}

class Meta : "cc.Meta" {
    string ver;
    string uuid;
    bool isGroup;
    string type;
    string wrapMode;
    string filterMode;
    variant subMetas;
internal:
    string _uuid;
    Meta@ subMetaList;
    void __ctor__() {
        if (subMetas) {
            subMetaList = get_sub_metas(this);
            _uuid = subMetaList[0].uuid;
        } else {
            _uuid = uuid;
        }
    }

    string get_uuid() {
        return _uuid;
    }
}

class SceneAsset : "cc.SceneAsset" extends Item {
    Id scene;

    void write_source() {
        Root.items[scene.__id__].write_setup_scene();
        Root.items[scene.__id__].write_create_scene();
    }
}

class Scene : "cc.Scene" extends Item {
    string id : "_id";
    bool autoReleaseAssets;

    void __ctor__() {
        name = "scene";
    }

    void write_setup_scene() {
        = {
        "void ", name, "::setupScene() {";
        > {
            "auto director = cocos2d::Director::getInstance();";
            "auto glview = director->getOpenGLView();";
            $ super.write_setup_scene();
        }
        "}";
        ;
        }
    }

    void write_create_scene() {
        = {
        "Scene* " + name + "::createScene() {";
        > {
            "auto scene = Scene::create();";
            autoReleaseAssets = autoReleaseAssets;
            $ super.write_create_scene();
            "return scene;";
        }
        "}";
        ;
        }
    }
}

class Canvas : "cc.Canvas" extends Item {
    Size _designResolution;
    bool _fitWidth;
    bool _fitHeight;
    void write_setup_scene() {
        = {
        "// cc.Canvas";
        "const auto designResolution = ", _designResolution, ";";
        string policy;
        if (_fitWidth && _fitHeight)
            policy = "ResolutionPolicy::SHOW_ALL";
        else if (_fitHeight)
            policy = "ResolutionPolicy::FIXED_HEIGHT";
        else if (_fitWidth)
            policy = "ResolutionPolicy::FIXED_WIDTH";
        else
            policy = "ResolutionPolicy::NO_BORDER";

        "glview->setDesignResolutionSize(designResolution.width, designResolution.height, ", policy, ");";
        }
        super.write_setup_scene();
    }
}

class Camera : "cc.Camera" extends Item  {
    int cullingMask : "_cullingMask" = -1;
    int clearFlags : "_clearFlags";
    Color4B backgroundColor : "_backgroundColor";
    int depth : "_depth";
    int zoomRatio : "_zoomRatio";
    Uuid targetTexture : "_targetTexture" = null;

    void write_create_scene() {
        = {
        "// cc.Camera";
        "auto ", Name, " = Camera::create();";
        Name.depth = depth;
//        Name.zoomRatio = zoomRatio;
        ;
        }
        super.write_create_scene();
    }
}

class Button : "cc.Button" extends Item {
    int transition;
    float duration;
    float zoomScale;

//background
    Color4B normalColor : "_N$normalColor";
    Color4B disabledColor : "_N$disabledColor";
    Color4B pressColor;
    Color4B hoverColor;

    Uuid normalSprite : "_N$normalSprite";
    Uuid disabledSprite : "_N$disabledSprite";
    Uuid pressedSprite;
    Uuid hoverSprite;

    Id target : "_N$target";
    bool pressedActionEnabled;

//events
    bool interactable : "_N$interactable";
    bool enableAutoGrayEffect : "_N$enableAutoGrayEffect";
    Id@ clickEvents;

internal:
    Sprite sprite;
    bool ignoreContentAdaptWithSize = false;

    void post_init() {
        super.post_init();
        sprite = Parent.get_component("cc.Sprite");
    }

    void write_create_scene() {
        "// cc.Button";
        if (sprite && sprite._spriteFrame) {
            = {
            string spriteFrameName = find_resource_by_uuid(sprite._spriteFrame.__uuid__);
            string pressedSpriteName = find_resource_by_uuid(pressedSprite.__uuid__);
            string disabledSpriteName = find_resource_by_uuid(disabledSprite.__uuid__);
            "/*", spriteFrameName, " uuid=", sprite._spriteFrame.__uuid__, "*/";
            "/*", pressedSpriteName, " uuid=", pressedSprite.__uuid__, "*/";
            "/*", disabledSpriteName, " uuid=", disabledSprite.__uuid__, "*/";
            "auto ", Name, " = ui::Button::create(";
                > {
                "\"",spriteFrameName, "\",";
                "\"", pressedSpriteName, "\",";
                "\"", disabledSpriteName, "\");";
                }
            }
        } else {
            = {
            "auto ", Name, " = ui::Button::create();";
            }
        }
        Parent.write_property(Name);
        = {
            Name.ignoreContentAdaptWithSize(ignoreContentAdaptWithSize);
            if(transition == 3) {
                Name.zoomScale = zoomScale;
                Name.pressedActionEnabled = true;
            }
        }

        super.write_create_scene();
    }
}

class EditBox : "cc.EditBox" extends Item {
    bool _useOriginalSize;
    string _string;
    float _tabIndex;
    Id@ editingDidBegan;
    Id@ textChanged;
    Id@ editingDidEnded;
    Id@ editingReturn;
    Uuid backgroundImage : "_N$backgroundImage";
    int returnType : "_N$returnType";
    int inputFlag : "_N$inputFlag";
    int inputMode : "_N$inputMode";
    int fontSize : "_N$fontSize";
    int lineHeight : "_N$lineHeight";
    Color4B fontColor : "_N$fontColor";
    string placeholder : "_N$placeholder";
    int placeholderFontSize : "_N$placeholderFontSize";
    Color4B placeholderFontColor : "_N$placeholderFontColor";
    int maxLength : "_N$maxLength";
    bool stayOnTop : "_N$stayOnTop";
}

class Label : "cc.Label" extends Item {
    bool _useOriginalSize;
    int _actualFontSize;
    int _fontSize;
    int _lineHeight;
    bool _enableWrapText;
    Uuid file : "_N$file";
    bool _isSystemFontUsed;
    int _spacingX;
    string _string : "_N$string";
    int horizontalAlign : "_N$horizontalAlign";
    int verticalAlign : "_N$verticalAlign";
    int overflow : "_N$overflow";
}

class ProgressBar : "cc.ProgressBar" extends Item {
    int totalLength : "_N$totalLength";
    Id barSprite : "_N$barSprite";
    int mode : "_N$mode";
    float progress : "_N$progress";
    bool reverse : "_N$reverse";
}

class ScrollView : "cc.ScrollView" extends Item {
    Id content;
    bool horizontal;
    bool vertical;
    bool inertia;
    float brake;
    bool elastic;
    float bounceDuration;
    Id@ scrollEvents;
    bool cancelInnerEvents;
    Id horizontalScrollBar : "_N$horizontalScrollBar";
    Id verticalScrollBar : "_N$verticalScrollBar";
}

class Slider : "cc.Slider" extends Item {
     int direction;
     Id@ slideEvents;
    Id handle : "_N$handle";
    int progress : "_N$progress";
}

class ParticleSystem : "cc.ParticleSystem" extends Item {
    bool _custom;
    Uuid _file;
    int _srcBlendFactor;
    int _dstBlendFactor;
    bool playOnLoad;
    bool _autoRemoveOnFinish;
    int _totalParticles;
    int _duration;
    int _emissionRate;
    int _life;
    int _lifeVar;
    Color4B _startColor;
    Color4B _startColorVar;
    Color4B _endColor;
    Color4B _endColorVar;
    int _angle;
    int _angleVar;
    int _startSize;
    int _startSizeVar;
    int _endSize;
    int _endSizeVar;
    int _startSpin;
    int _startSpinVar;
    int _endSpin;
    int _endSpinVar;
    Vec2 _sourcePos;
    Vec2 _posVar;
    int _positionType;
    int _emitterMode;
    Vec2 _gravity;
    int _speed;
    int _speedVar;
    int _tangentialAccel;
    int _tangentialAccelVar;
    int _radialAccel;
    int _radialAccelVar;
    bool _rotationIsDir;
    int _startRadius;
    int _startRadiusVar;
    int _endRadius;
    int _endRadiusVar;
    int _rotatePerS;
    int _rotatePerSVar;
    bool preview : "_N$preview";
}

class Sprite : "cc.Sprite" extends Item {
    Uuid _spriteFrame;
    int _type;
    int _sizeMode;
    int _fillType;
    Vec2 _fillCenter;
    int _fillStart;
    int _fillRange;
    bool _isTrimmedMode;
    int _srcBlendFactor;
    int _dstBlendFactor;
    Uuid _atlas;
}

class Skeleton : "sp.Skeleton" extends Item {
    bool _paused;
    string defaultSkin;
    string defaultAnimation;
    bool loop;
    bool _premultipliedAlpha;
    Uuid skeletonData : "_N$skeletonData";
    int timeScale : "_N$timeScale";
    bool debugSlots : "_N$debugSlots";
    bool debugBones : "_N$debugBones";
}

class TileMap : "cc.TiledMap" extends Item {
    Uuid _tmxFile;
}

class Mask : "cc.Mask" extends Item {
    int _type;
    int _segements;
    Uuid spriteFrame : "_N$spriteFrame";
    float alphaThreshold : "_N$alphaThreshold";
    bool inverted : "_N$inverted";
}

class PageView : "cc.PageView" extends Item {
    Id content;
    bool horizontal;
    bool vertical;
    bool inertia;
    float brake;
    bool elastic;
    float bounceDuration;
    Id@ scrollEvents;
    bool cancelInnerEvents;
    float scrollThreshold;
    int autoPageTurningThreshold;
    float pageTurningEventTiming;
    Id@ pageEvents;
    int sizeMode : "_N$sizeMode";
    int direction : "_N$direction";
    Id indicator : "_N$indicator";
}

class Prefab : "cc.Prefab" {
    Item@ nodes;
}

class RichText : "cc.RichText" extends Item {
    string _string : "_N$string";
    int horizontalAlign : "_N$horizontalAlign";
    int fontSize : "_N$fontSize";
    Uuid font : "_N$font";
    int maxWidth : "_N$maxWidth";
    int lineHeight : "_N$lineHeight";
    Uuid imageAtlas : "_N$imageAtlas";
    bool handleTouchEvent : "_N$handleTouchEvent";
}

class Toggle : "cc.Toggle" extends Button {
    Id toggleGroup;
    Id checkMark;
    Id@ checkEvents;
    bool isChecked : "_N$isChecked";
}

class ToggleGroup : "cc.ToggleGroup" extends Item {
    bool allowSwitchOff;
}

class VideoPlayer : "cc.VideoPlayer" extends Item {
    int _resourceType;
    string _remoteURL;
    Uuid _clip;
    Id@ videoPlayerEvent;
    bool keepAspectRatio : "_N$keepAspectRatio";
    bool isFullscreen : "_N$isFullscreen";
}

class WebView : "cc.WebView" extends Item {
    bool _useOriginalSize;
    string _url;
    Id@ webviewEvents;
}

class ArmatureDisplay : "dragonBones.ArmatureDisplay" extends Item {
    string _armatureName;
    string _animationName;
    int playTimes;
    Uuid dragonAsset : "_N$dragonAsset";
    Uuid dragonAtlasAsset : "_N$dragonAtlasAsset";
    int _defaultArmatureIndex : "_N$_defaultArmatureIndex";
    int _animationIndex : "_N$_animationIndex";
    int timeScale : "_N$timeScale";
    bool debugBones : "_N$debugBones";
}

class BoxCollider : "cc.BoxCollider" extends Item {
    Vec2 _offset;
    Size _size;
}

class CircleCollider : "cc.CircleCollider" extends Item {
    Vec2 _offset;
    Vec2@ points;
}

class PolygonCollider : "cc.PolygonCollider" extends Item {
    Vec2 _offset;
    Size _size;
}

class LabelOutline : "cc.LabelOutline" extends Item {
    Color4B color;
    float width;
}

class Layout : "cc.Layout" extends Item {
    Size _layoutSize;
    int _resize;
    int layoutType : "_N$layoutType";
    int padding : "_N$padding";
    Size cellSize : "_N$cellSize";
    int startAxis : "_N$startAxis";
    int paddingLeft : "_N$paddingLeft";
    int paddingRight : "_N$paddingRight";
    int paddingTop : "_N$paddingTop";
    int paddingBottom : "_N$paddingBottom";
    int spacingX : "_N$spacingX";
    int spacingY : "_N$spacingY";
    int verticalDirection : "_N$verticalDirection";
    int horizontalDirection : "_N$horizontalDirection";
}

class MotionStreak : "cc.MotionStreak" extends Item {
    int _fadeTime;
    int _minSeg;
    int _stroke;
    Uuid _texture;
    Color4B _color;
    bool _fastMode;
    bool preview : "_N$preview";
}

class PageViewIndicator : "cc.PageViewIndicator" extends Item
{
    string _layout;
    Id _pageView;
    Id@ _indicators;
    Uuid spriteFrame;
    int direction;
    Size cellSize;
    int spacing;
}

class PrefabInfo : "cc.PrefabInfo" {
    Id root;
    Uuid asset;
    string fileId;
    bool sync;
}

class Scrollbar : "cc.Scrollbar" extends Item {
    Id _scrollView;
    bool _touching;
    int _opacity;
    bool enableAutoHide;
    int autoHideTime;
    Id handle;
    int direction;
}

class Animation : "cc.Animation" extends Item {
    Uuid _defaultClip;
    Uuid@ _clips;
    bool playOnLoad;
}

class Widget : "cc.Widget" extends Item {
    bool isAlignOnce;
    string _target;
    int _alignFlags;
    float _left;
    float _right;
    float _top;
    float _bottom;
    int _verticalCenter;
    int _horizontalCenter;
    bool _isAbsLeft;
    bool _isAbsRight;
    bool _isAbsTop;
    bool _isAbsBottom;
    bool _isAbsHorizontalCenter;
    bool _isAbsVerticalCenter;
    int _originalWidth;
    int _originalHeight;
}

class ClickEvent : "cc.ClickEvent" {
    Id target;
    string component;
    string handler;
    string customEventData;
}

class AnimationFrameInt {
    float frame;
    int value;
}

class AnimationFrameFloat {
    float frame;
    float value;
}

class AnimationFrameVec2 {
    float frame;
    Vec2 value;
}

class AnimationFramePosition {
    float frame;
    int@ value;
    int@ motionPath;
    string curve;
}

class AnimationFrameColor {
    float frame;
    Color4B value;
}

class AnimationFrameUuid {
    float frame;
    Uuid value;
}

class AnimationFrameBool {
    float frame;
    bool value;
}

class AnimationCurveProp {
    AnimationFrameInt@ rotation;
    AnimationFramePosition@ position;
    AnimationFrameFloat@ scaleX;
    AnimationFrameFloat@ scaleY;
    AnimationFrameInt@ width;
    AnimationFrameInt@ height;
    AnimationFrameColor@ color;
    AnimationFrameInt@ opacity;
    AnimationFrameFloat@ anchorX;
    AnimationFrameFloat@ anchorY;
    AnimationFrameFloat@ skewX;
    AnimationFrameFloat@ skewY;
}

class AnimationSpriteFrames {
    AnimationFrameBool@ enabled;
    AnimationFrameUuid@ spriteFrame;
    AnimationFrameInt@ fillType;
    AnimationFrameVec2@ fillCenter;
    AnimationFrameInt@ fillStart;
    AnimationFrameInt@ fillRange;
}

class AnimationComps {
    AnimationSpriteFrames sprite : "cc.Sprite";
}

class AnimationCurveData {
    AnimationCurveProp props;
    AnimationComps comps;
    Id@ event;
}

class TiledLayer : "cc.TiledLayer" extends Item {
}

class AnimationClip : "cc.AnimationClip" {
  float _duration;
  int sample;
  int speed;
  int wrapMode;
  AnimationCurveData curveData;
}
