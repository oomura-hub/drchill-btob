from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import numpy as np

BG="assets/_gen/darts2.png"
FIX="assets/fv-fixture-lineup.png"
OUT="assets/case-ws-darts.jpg"

# --- tunables (counter placement) ---
CX=0.355      # fixture center x (front-right empty counter)
BASE=0.83     # fixture base y (where it meets counter)
WF=0.255      # fixture width fraction
BRIGHT=0.9
WARM=(1.0,0.97,0.90)
SHADOW=150
# ------------------------------------

fx0=Image.open(FIX).convert("RGBA")
a=np.array(fx0)[:,:,3]; ys=np.where(a.max(axis=1)>20)[0]; xs=np.where(a.max(axis=0)>20)[0]
fx0=fx0.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))

bg=Image.open(BG).convert("RGBA"); W,H=bg.size
fw=int(W*WF); fh=int(fx0.height*fw/fx0.width)
fix=ImageEnhance.Brightness(fx0).enhance(BRIGHT)
r,g,b,al=fix.split()
r=r.point(lambda v:int(v*WARM[0])); g=g.point(lambda v:int(v*WARM[1])); b=b.point(lambda v:int(v*WARM[2]))
fix=Image.merge("RGBA",(r,g,b,al)).resize((fw,fh),Image.LANCZOS)
cx=int(W*CX); base=int(H*BASE); x=cx-fw//2; y=base-fh

# reflection on counter
refl=fix.transpose(Image.FLIP_TOP_BOTTOM)
rh=int(fh*0.28); refl=refl.crop((0,0,fw,rh))
grad=Image.new("L",(1,rh),0)
for yy in range(rh): grad.putpixel((0,yy),int(60*(1-yy/rh)))
grad=grad.resize((fw,rh))
rr,rg,rb,ra=refl.split()
ra=Image.fromarray((np.array(ra).astype(float)*(np.array(grad)/255.0)).astype('uint8'))
refl=Image.merge("RGBA",(rr,rg,rb,ra))
rl=Image.new("RGBA",(W,H),(0,0,0,0)); rl.paste(refl,(x,base+2),refl); rl=rl.filter(ImageFilter.GaussianBlur(1.5))
bg=Image.alpha_composite(bg,rl)

# contact shadow
sh=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
ew=int(fw*1.1); eh=int(fh*0.07); d.ellipse([cx-ew//2,base-eh//2,cx+ew//2,base+eh//2],fill=(0,0,0,SHADOW))
sh=sh.filter(ImageFilter.GaussianBlur(16)); bg=Image.alpha_composite(bg,sh)
# drop shadow
sil=Image.new("RGBA",(W,H),(0,0,0,0)); blk=Image.new("RGBA",(fw,fh),(0,0,0,120)); sil.paste(blk,(x+5,y+8),fix.split()[3]); sil=sil.filter(ImageFilter.GaussianBlur(14))
bg=Image.alpha_composite(bg,sil)
# fixture
lay=Image.new("RGBA",(W,H),(0,0,0,0)); lay.paste(fix,(x,y),fix); bg=Image.alpha_composite(bg,lay)

# crop 4:3
tw,th=W,int(W*3/4)
if th>H: th=H; tw=int(H*4/3)
left=(W-tw)//2; top=(H-th)
bg=bg.crop((left,top,left+tw,top+th)).convert("RGB").resize((1200,900),Image.LANCZOS)
# subtle photographic grain to unify
arr=np.array(bg).astype(np.int16)
noise=np.random.default_rng(7).normal(0,4.0,arr.shape).astype(np.int16)
arr=np.clip(arr+noise,0,255).astype('uint8')
Image.fromarray(arr).save(OUT,quality=88)
print("saved",OUT)
