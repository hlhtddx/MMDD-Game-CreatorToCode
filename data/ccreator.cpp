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
    Size designResolution : "_designResolution";
    bool fitWidth : "_fitWidth";
    bool fitHeight : "_fitHeight";
    void write_setup_scene() {
        = {
        "// cc.Canvas";
        "const auto designResolution = ", designResolution, ";";
        string policy;
        if (fitWidth && fitHeight)
            policy = "ResolutionPolicy::SHOW_ALL";
        else if (fitHeight)
            policy = "ResolutionPolicy::FIXED_HEIGHT";
        else if (fitWidth)
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
        if (sprite && sprite.spriteFrame) {
            = {
            string spriteFrameName = find_resource_by_uuid(sprite.spriteFrame.__uuid__);
            string pressedSpriteName = find_resource_by_uuid(pressedSprite.__uuid__);
            string disabledSpriteName = find_resource_by_uuid(disabledSprite.__uuid__);
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
    bool useOriginalSize : "_useOriginalSize";
    string _string;
    float tabIndex : "_tabIndex";
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
    bool useOriginalSize : "_useOriginalSize";
    int actualFontSize : "_actualFontSize";
    int fontSize : "_fontSize";
    int lineHeight : "_lineHeight";
    bool enableWrapText : "_enableWrapText";
    Uuid file : "_N$file";
    bool isSystemFontUsed : "_isSystemFontUsed";
    int spacingX : "_spacingX";
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
    bool custom : "_custom";
    Uuid file : "_file";
    int srcBlendFactor : "_srcBlendFactor";
    int dstBlendFactor : "_dstBlendFactor";
    bool playOnLoad;
    bool autoRemoveOnFinish : "_autoRemoveOnFinish";
    int totalParticles : "_totalParticles";
    int duration : "_duration";
    int emissionRate : "_emissionRate";
    int life : "_life";
    int lifeVar : "_lifeVar";
    Color4B startColor : "_startColor";
    Color4B startColorVar : "_startColorVar";
    Color4B endColor : "_endColor";
    Color4B endColorVar : "_endColorVar";
    int angle : "_angle";
    int angleVar : "_angleVar";
    int startSize : "_startSize";
    int startSizeVar : "_startSizeVar";
    int endSize : "_endSize";
    int endSizeVar : "_endSizeVar";
    int startSpin : "_startSpin";
    int startSpinVar : "_startSpinVar";
    int endSpin : "_endSpin";
    int endSpinVar : "_endSpinVar";
    Vec2 sourcePos : "_sourcePos";
    Vec2 posVar : "_posVar";
    int positionType : "_positionType";
    int emitterMode : "_emitterMode";
    Vec2 gravity : "_gravity";
    int speed : "_speed";
    int speedVar : "_speedVar";
    int tangentialAccel : "_tangentialAccel";
    int tangentialAccelVar : "_tangentialAccelVar";
    int radialAccel : "_radialAccel";
    int radialAccelVar : "_radialAccelVar";
    bool rotationIsDir : "_rotationIsDir";
    int startRadius : "_startRadius";
    int startRadiusVar : "_startRadiusVar";
    int endRadius : "_endRadius";
    int endRadiusVar : "_endRadiusVar";
    int rotatePerS : "_rotatePerS";
    int rotatePerSVar : "_rotatePerSVar";
    bool preview : "_N$preview";
}

class Sprite : "cc.Sprite" extends Item {
    Uuid spriteFrame : "_spriteFrame";
    int type : "_type";
    int sizeMode : "_sizeMode";
    int fillType : "_fillType";
    Vec2 fillCenter : "_fillCenter";
    int fillStart : "_fillStart";
    int fillRange : "_fillRange";
    bool isTrimmedMode : "_isTrimmedMode";
    int srcBlendFactor : "_srcBlendFactor";
    int dstBlendFactor : "_dstBlendFactor";
    Uuid atlas : "_atlas";
}

class Skeleton : "sp.Skeleton" extends Item {
    bool paused : "_paused";
    string defaultSkin;
    string defaultAnimation;
    bool loop;
    bool premultipliedAlpha : "_premultipliedAlpha";
    Uuid skeletonData : "_N$skeletonData";
    int timeScale : "_N$timeScale";
    bool debugSlots : "_N$debugSlots";
    bool debugBones : "_N$debugBones";
}

class TileMap : "cc.TiledMap" extends Item {
    Uuid tmxFile : "_tmxFile";
}

class Mask : "cc.Mask" extends Item {
    int type : "_type";
    int segements : "_segements";
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
    int resourceType : "_resourceType";
    string remoteURL : "_remoteURL";
    Uuid clip : "_clip";
    Id@ videoPlayerEvent;
    bool keepAspectRatio : "_N$keepAspectRatio";
    bool isFullscreen : "_N$isFullscreen";
}

class WebView : "cc.WebView" extends Item {
    bool useOriginalSize : "_useOriginalSize";
    string url : "_url";
    Id@ webviewEvents;
}

class ArmatureDisplay : "dragonBones.ArmatureDisplay" extends Item {
    string armatureName : "_armatureName";
    string animationName : "_animationName";
    int playTimes;
    Uuid dragonAsset : "_N$dragonAsset";
    Uuid dragonAtlasAsset : "_N$dragonAtlasAsset";
    int _defaultArmatureIndex : "_N$_defaultArmatureIndex";
    int _animationIndex : "_N$_animationIndex";
    int timeScale : "_N$timeScale";
    bool debugBones : "_N$debugBones";
}

class BoxCollider : "cc.BoxCollider" extends Item {
    Vec2 offset : "_offset";
    Size size : "_size";
}

class CircleCollider : "cc.CircleCollider" extends Item {
    Vec2 offset : "_offset";
    Vec2@ points;
}

class PolygonCollider : "cc.PolygonCollider" extends Item {
    Vec2 offset : "_offset";
    Size size : "_size";
}

class LabelOutline : "cc.LabelOutline" extends Item {
    Color4B color;
    float width;
}

class Layout : "cc.Layout" extends Item {
    Size layoutSize : "_layoutSize";
    int resize : "_resize";
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
    int fadeTime : "_fadeTime";
    int minSeg : "_minSeg";
    int stroke : "_stroke";
    Uuid texture : "_texture";
    Color4B color : "_color";
    bool fastMode : "_fastMode";
    bool preview : "_N$preview";
}

class PageViewIndicator : "cc.PageViewIndicator" extends Item
{
    string layout : "_layout";
    Id pageView : "_pageView";
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
    Id scrollView : "_scrollView";
    bool touching : "_touching";
    int opacity : "_opacity";
    bool enableAutoHide;
    int autoHideTime;
    Id handle;
    int direction;
}

class Animation : "cc.Animation" extends Item {
    Uuid defaultClip : "_defaultClip";
    Uuid@ _clips;
    bool playOnLoad;
}

class Widget : "cc.Widget" extends Item {
    bool isAlignOnce;
    string target : "_target";
    int alignFlags : "_alignFlags";
    float left : "_left";
    float right : "_right";
    float top : "_top";
    float bottom : "_bottom";
    int verticalCenter : "_verticalCenter";
    int horizontalCenter : "_horizontalCenter";
    bool isAbsLeft : "_isAbsLeft";
    bool isAbsRight : "_isAbsRight";
    bool isAbsTop : "_isAbsTop";
    bool isAbsBottom : "_isAbsBottom";
    bool isAbsHorizontalCenter : "_isAbsHorizontalCenter";
    bool isAbsVerticalCenter : "_isAbsVerticalCenter";
    int originalWidth : "_originalWidth";
    int originalHeight : "_originalHeight";
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
  float duration : "_duration";
  int sample;
  int speed;
  int wrapMode;
  AnimationCurveData curveData;
}
