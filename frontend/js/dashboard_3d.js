const container = document.getElementById('3d-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// 创建赛博朋克风格的线框球体
const geometry = new THREE.IcosahedronGeometry(2, 2);
const material = new THREE.MeshBasicMaterial({ 
    color: 0x00f3ff, 
    wireframe: true, 
    transparent: true, 
    opacity: 0.8 
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);

camera.position.z = 5;

// 动画循环
function animate() {
    requestAnimationFrame(animate);
    sphere.rotation.x += 0.005;
    sphere.rotation.y += 0.01;
    
    // 逐渐恢复原本颜色 (绿色/蓝色)
    if (material.color.getHex() !== 0x00f3ff) {
        material.color.lerp(new THREE.Color(0x00f3ff), 0.05);
    }
    
    renderer.render(scene, camera);
}
animate();

// 暴露给 app.js 的接口，当检测到异常时触发
window.triggerThreatAnimation = function(intensity) {
    // 遇到异常变成红色，并放大
    material.color.setHex(0xff0041);
    sphere.scale.set(1.2, 1.2, 1.2);
    
    // 0.5秒后恢复大小
    setTimeout(() => {
        sphere.scale.set(1, 1, 1);
    }, 500);
};

// 监听窗口大小改变
window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});