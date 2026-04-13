import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import traceback

class VLMAnalyzer:
    def __init__(self, model_id="microsoft/Florence-2-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.ready = False
        self.model = None
        self.processor = None
        
        print(f"\n{'='*60}")
        print(f"🧠 初始化 VLM (视觉语言模型)")
        print(f"{'='*60}")
        print(f"   模型: {model_id}")
        print(f"   设备: {self.device}")
        print(f"   数据类型: {self.torch_dtype}")
        print(f"\n   ⏳ 正在加载模型...")
        
        try:
            # 加载模型（首次运行会下载约 500MB）
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True,
                torch_dtype=self.torch_dtype
            ).to(self.device).eval()
            
            # 加载处理器
            self.processor = AutoProcessor.from_pretrained(
                model_id, 
                trust_remote_code=True
            )
            
            self.ready = True
            
            print(f"   ✅ VLM 模型加载成功！")
            print(f"   模型参数量: {sum(p.numel() for p in self.model.parameters()):,}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            self.ready = False
            print(f"\n   ❌ VLM 模型加载失败!")
            print(f"   错误信息: {str(e)}")
            print(f"\n   可能的原因:")
            print(f"   1. 网络连接问题（无法下载模型）")
            print(f"   2. 显存不足（Florence-2 需要 ~2GB 显存）")
            print(f"   3. 缺少依赖包（请安装: pip install transformers torch）")
            print(f"\n   详细错误:")
            traceback.print_exc()
            print(f"\n{'='*60}\n")

    def describe_scene(self, image_np, task_prompt="<CAPTION>"):
        if not self.ready or not self.model or not self.processor:
            return "VLM Not Ready"
        
        try:
            image = Image.fromarray(image_np)
            inputs = self.processor(
                text=task_prompt, 
                images=image, 
                return_tensors="pt"
            ).to(self.device, self.torch_dtype)
            
            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                num_beams=3,
                do_sample=False
            )
            
            generated_text = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]
            
            return generated_text
            
        except Exception as e:
            print(f"❌ VLM 推理错误: {e}")
            return f"VLM Inference Error: {str(e)}"

# 单例化（延迟初始化，避免启动时阻塞）
vlm_instance = None

def get_vlm_instance():
    """获取 VLM 实例（延迟初始化）"""
    global vlm_instance
    if vlm_instance is None:
        vlm_instance = VLMAnalyzer()
    return vlm_instance

# 启动时立即初始化
try:
    vlm_instance = get_vlm_instance()
except Exception as e:
    print(f"⚠️  VLM 初始化异常: {e}")
    vlm_instance = VLMAnalyzer.__new__(VLMAnalyzer)
    vlm_instance.ready = False