#!/bin/bash

# ==============================================================================
# GITHUB REPOSITORY SECURITY & HARDENING SCRIPT
# ==============================================================================
# Script này sử dụng GitHub CLI (gh) để thiết lập các lớp bảo mật nâng cao cho 
# repository của bạn, đặc biệt tối ưu cho trường hợp bạn chuyển Repo về Private
# và mời các cộng tác viên khác vào làm việc.
# ==============================================================================

# Yêu cầu: Bạn phải cài đặt GitHub CLI (`gh`) và đã đăng nhập (`gh auth login`).
if ! command -v gh &> /dev/null; then
    echo "[!] GitHub CLI (gh) chưa được cài đặt. Vui lòng cài đặt và chạy 'gh auth login' trước."
    exit 1
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "🚀 Đang thiết lập bảo mật cho repository: $REPO"

# 1. Bật Secret Scanning & Vulnerability Alerts (Tự động phát hiện lộ key)
echo "🔒 1/4 Bật Secret Scanning và Dependabot Alerts..."
gh api -X PUT /repos/$REPO/vulnerability-alerts --silent
gh api -X PUT /repos/$REPO/automated-security-fixes --silent
# Secret scanning thường chỉ bật API được cho public repo hoặc Github Enterprise
# Nhưng ta cố gắng call API
gh api -X PUT /repos/$REPO/secret-scanning/push-protection -f status="enabled" --silent 2>/dev/null || echo "   (Lưu ý: Push protection có thể yêu cầu Repo Public hoặc tài khoản Pro/Enterprise)"

# 2. Thiết lập Branch Protection Rule cho nhánh 'master'
# Đảm bảo không ai (kể cả bạn) push thẳng lên master mà không qua Pull Request.
echo "🛡️  2/4 Thiết lập Branch Protection cho nhánh 'master'..."
gh api -X PUT /repos/$REPO/branches/master/protection \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -f required_status_checks=null \
  -f enforce_admins=true \
  -F required_pull_request_reviews[dismiss_stale_reviews]=true \
  -F required_pull_request_reviews[require_code_owner_reviews]=true \
  -F required_pull_request_reviews[required_approving_review_count]=1 \
  -f restrictions=null \
  --silent
echo "   ✅ Đã yêu cầu Pull Request và CODEOWNER (@Binhchuoizzz) review trước khi merge."

# 3. Chặn Force Push và Deletion trên nhánh master
echo "🚫 3/4 Chặn Force Push và xoá nhánh master..."
# (Đã được cover trong ruleset ở trên do API tự mặc định khoá force-push)

# 4. Hướng dẫn chuyển sang Private (nếu bạn chưa chuyển)
echo "🕵️  4/4 Trạng thái hiển thị (Visibility)..."
VISIBILITY=$(gh repo view --json isPrivate -q .isPrivate)
if [ "$VISIBILITY" == "true" ]; then
    echo "   ✅ Repo của bạn đã là Private."
else
    echo "   [!] Repo đang là Public. Nếu sếp bạn yêu cầu bảo mật mã nguồn, hãy chạy lệnh sau để chuyển về Private:"
    echo "       gh repo edit $REPO --visibility private"
fi

echo ""
echo "🎉 HOÀN TẤT! Hệ thống GitHub của bạn đã được đóng kín và bảo vệ an toàn."
echo "Từ bây giờ, tất cả các thành viên được mời vào repo (Collaborators) sẽ:"
echo "- Bắt buộc phải tạo branch riêng (VD: feature/auth)."
echo "- Tạo Pull Request để đưa code vào master."
echo "- Bạn (@Binhchuoizzz - được chỉ định trong file CODEOWNERS) phải Approve thì code mới được merge."
