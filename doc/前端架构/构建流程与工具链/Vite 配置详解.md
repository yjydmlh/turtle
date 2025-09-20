# Vite 配置详解

<cite>
**本文档引用的文件**   
- [vite.config.js](file://frontend/vite.config.js)
- [package.json](file://frontend/package.json)
- [api.js](file://frontend/src/lib/api.js)
- [performance_optimization.md](file://frontend/performance_optimization.md)
</cite>

## 目录
1. [开发服务器配置](#开发服务器配置)
2. [构建优化配置](#构建优化配置)
3. [依赖预构建配置](#依赖预构建配置)
4. [性能调优策略](#性能调优策略)
5. [环境变量注入机制](#环境变量注入机制)
6. [常见问题排查指南](#常见问题排查指南)

## 开发服务器配置

Vite 开发服务器配置旨在提升开发体验和性能，通过 HMR 热更新、代理设置和 API 请求转发机制实现高效的开发流程。

```mermaid
flowchart TD
Client["前端客户端 (http://localhost:3000)"] --> Server["Vite 开发服务器"]
Server --> Proxy["API 代理"]
Proxy --> Backend["后端服务 (http://localhost:8000)"]
subgraph "开发服务器功能"
HMR["HMR 热更新\n端口: 3001\noverlay: false"]
Warmup["文件预热\n./src/lib/components/*.svelte\n./src/routes/*.svelte"]
FS["文件系统访问\nallow: ['..', '..']"]
end
Server --> HMR
Server --> Warmup
Server --> FS
Proxy --> Cache["代理缓存\nCache-Control: public, max-age=300"]
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L10-L45)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L10-L45)
- [api.js](file://frontend/src/lib/api.js#L1-L10)

## 构建优化配置

构建优化配置通过代码分割策略、压缩工具选择和构建目标设置，提升生产环境下的打包性能和加载速度。

```mermaid
graph TD
Build["构建配置"] --> Target["构建目标\ntarget: es2020"]
Build --> Minify["压缩工具\nminify: esbuild"]
Build --> Sourcemap["源码映射\nsourcemap: false"]
Build --> ChunkSize["代码块大小警告阈值\nchunkSizeWarningLimit: 1000"]
Rollup["Rollup 选项"] --> ManualChunks["手动代码分割"]
ManualChunks --> Charts["klinecharts → charts"]
ManualChunks --> Icons["lucide-svelte → icons"]
ManualChunks --> Vendor["node_modules → vendor"]
Output["输出配置"] --> Naming["文件命名策略\nassets/[name]-[hash].[ext]"]
Build --> Rollup
Rollup --> Output
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L48-L72)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L48-L72)
- [performance_optimization.md](file://frontend/performance_optimization.md#L20-L35)

## 依赖预构建配置

依赖预构建配置通过提前构建和缓存第三方依赖，显著提升开发服务器的启动速度和首次加载性能。

```mermaid
classDiagram
class OptimizeDeps {
+include : string[]
+force : boolean
+exclude : string[]
}
class IncludedDeps {
+klinecharts
+lucide-svelte
+clsx
+tailwind-merge
}
OptimizeDeps --> IncludedDeps : 包含
OptimizeDeps --> ExcludedDeps : 排除
class ExcludedDeps {
无
}
note right of OptimizeDeps
force : true
强制预构建以提升性能
end note
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L74-L79)
- [package.json](file://frontend/package.json#L25-L28)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L74-L79)
- [package.json](file://frontend/package.json#L25-L28)
- [performance_optimization.md](file://frontend/performance_optimization.md#L12-L18)

## 性能调优策略

性能调优策略综合运用多种技术手段，包括 HMR 优化、warmup 预热、压缩工具选择和构建目标设置，全面提升开发体验与构建性能。

```mermaid
flowchart LR
Performance["性能调优策略"] --> Development["开发阶段"]
Performance --> Production["生产阶段"]
Development --> HMR["HMR 热更新优化\n独立端口 3001\n减少 overlay 影响"]
Development --> Warmup["文件预热\n预加载常用组件"]
Development --> Cache["开发缓存\nforce: true"]
Production --> Esbuild["esbuild 压缩\n快速构建"]
Production --> Target["构建目标 es2020\n平衡兼容性与性能"]
Production --> Splitting["代码分割\nmanualChunks 策略"]
Production --> Naming["文件命名\n[hash] 缓存优化"]
style Development fill:#f9f,stroke:#333
style Production fill:#bbf,stroke:#333
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L10-L22)
- [vite.config.js](file://frontend/vite.config.js#L48-L72)
- [vite.config.js](file://frontend/vite.config.js#L83-L86)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L10-L22)
- [vite.config.js](file://frontend/vite.config.js#L48-L72)
- [vite.config.js](file://frontend/vite.config.js#L83-L86)
- [performance_optimization.md](file://frontend/performance_optimization.md#L1-L100)

## 环境变量注入机制

环境变量注入机制在构建时将版本信息和构建时间注入到应用程序中，便于版本追踪和调试。

```mermaid
sequenceDiagram
participant Build as 构建过程
participant Define as define 配置
participant App as 应用程序
Build->>Define : 读取 npm_package_version
alt 版本存在
Define->>Define : 使用实际版本号
else 版本不存在
Define->>Define : 使用默认值 '1.0.0'
end
Build->>Define : 获取当前时间戳
Define->>Define : 格式化为 ISO 字符串
Define->>App : 注入 __APP_VERSION__
Define->>App : 注入 __BUILD_TIME__
App->>App : 在代码中使用常量
Note over App : 可用于版本追踪和调试
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L88-L91)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L88-L91)
- [package.json](file://frontend/package.json#L2-L3)

## 常见问题排查指南

针对开发过程中常见的跨域代理失败、依赖加载缓慢等问题提供详细的排查和解决方案。

```mermaid
flowchart TD
Problems["常见问题"] --> CORS["跨域代理失败"]
Problems --> Slow["依赖加载缓慢"]
Problems --> HMR["HMR 热更新不工作"]
Problems --> Build["构建失败或缓慢"]
CORS --> CheckTarget["检查 target 配置是否正确"]
CORS --> CheckOrigin["确认 changeOrigin: true"]
CORS --> CheckSecure["secure: false 用于本地开发"]
CORS --> Network["检查网络连接和后端服务状态"]
Slow --> CheckInclude["确认 optimizeDeps.include 配置"]
Slow --> ForceRebuild["删除 node_modules/.vite 重新构建"]
Slow --> CheckNetwork["检查网络下载速度"]
Slow --> Analyze["使用性能分析工具定位瓶颈"]
HMR --> CheckPort["确认 HMR 端口未被占用"]
HMR --> CheckConfig["检查 hmr 配置是否正确"]
HMR --> Restart["重启开发服务器"]
HMR --> Firewall["检查防火墙设置"]
Build --> CheckTarget["确认 target 兼容性"]
Build --> CheckMinify["验证 minify 配置"]
Build --> DiskSpace["检查磁盘空间"]
Build --> Memory["确保足够内存"]
```

**图示来源**
- [vite.config.js](file://frontend/vite.config.js#L24-L39)
- [vite.config.js](file://frontend/vite.config.js#L74-L79)

**本节来源**
- [vite.config.js](file://frontend/vite.config.js#L24-L39)
- [vite.config.js](file://frontend/vite.config.js#L74-L79)
- [api.js](file://frontend/src/lib/api.js#L1-L10)
- [performance_optimization.md](file://frontend/performance_optimization.md#L101-L172)