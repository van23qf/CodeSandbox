#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[构建]${NC} $*"; }
warn()  { echo -e "${YELLOW}[警告]${NC} $*"; }
error() { echo -e "${RED}[错误]${NC} $*"; }

SANDBOX_IMAGES=(
    "docker/python:codesandbox-python:latest"
    "docker/nodejs:codesandbox-nodejs:latest"
)
PROJECT_IMAGE="codesandbox:latest"

build_sandbox_images() {
    for entry in "${SANDBOX_IMAGES[@]}"; do
        IFS=':' read -r context name tag <<< "$entry"
        image="${name}:${tag}"
        info "构建沙盒镜像 ${image} (上下文: ${context})"
        if docker build -t "$image" "$context"; then
            info "沙盒镜像 ${image} 构建完成"
        else
            error "沙盒镜像 ${image} 构建失败"
            return 1
        fi
    done
}

build_project_image() {
    info "构建项目镜像 ${PROJECT_IMAGE}"
    if docker build -t "$PROJECT_IMAGE" .; then
        info "项目镜像 ${PROJECT_IMAGE} 构建完成"
    else
        error "项目镜像 ${PROJECT_IMAGE} 构建失败"
        return 1
    fi
}

list_images() {
    echo ""
    info "已构建镜像列表:"
    echo "  沙盒镜像:"
    for entry in "${SANDBOX_IMAGES[@]}"; do
        IFS=':' read -r _ name tag <<< "$entry"
        image="${name}:${tag}"
        if docker image inspect "$image" &>/dev/null; then
            size=$(docker image inspect "$image" --format '{{.Size}}' 2>/dev/null)
            mb=$((size / 1024 / 1024))
            echo -e "    ${GREEN}${image}${NC}  (${mb}MB)"
        else
            echo -e "    ${RED}${image}  (未构建)${NC}"
        fi
    done
    echo "  项目镜像:"
    if docker image inspect "$PROJECT_IMAGE" &>/dev/null; then
        size=$(docker image inspect "$PROJECT_IMAGE" --format '{{.Size}}' 2>/dev/null)
        mb=$((size / 1024 / 1024))
        echo -e "    ${GREEN}${PROJECT_IMAGE}${NC}  (${mb}MB)"
    else
        echo -e "    ${RED}${PROJECT_IMAGE}  (未构建)${NC}"
    fi
}

usage() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  all       构建沙盒镜像 + 项目镜像 (默认)"
    echo "  sandbox   仅构建沙盒镜像 (codesandbox-python, codesandbox-nodejs)"
    echo "  project   仅构建项目镜像 (codesandbox)"
    echo "  list      列出镜像构建状态"
    echo "  help      显示帮助信息"
}

main() {
    local cmd="${1:-all}"

    if ! command -v docker &>/dev/null; then
        error "未找到 docker 命令，请先安装 Docker"
        exit 1
    fi

    if ! docker info &>/dev/null; then
        error "Docker 守护进程未运行"
        exit 1
    fi

    case "$cmd" in
        all)
            build_sandbox_images
            build_project_image
            list_images
            ;;
        sandbox)
            build_sandbox_images
            list_images
            ;;
        project)
            build_project_image
            list_images
            ;;
        list)
            list_images
            ;;
        help|-h|--help)
            usage
            ;;
        *)
            error "未知命令: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"
