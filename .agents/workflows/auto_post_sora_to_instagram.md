---
description: Soraで動画を作成し、Googleドライブに保存後、Instagramに自動投稿するワークフロー
---

このワークフローは、指定されたプロンプトに基づいてSora（または代替手段）で動画を生成し、Google Driveにバックアップとして保存した後、Instagramに自動で投稿する手順を定義します。

1. **動画生成の準備**:
現在、Soraは一般公開されたAPIがないため、ローカルにある動画ファイルを「生成された動画」として代用するか、ブラウザ操作エージェントを使用してSoraへのアクセスを試みます。ここでは既存の動画ファイルを利用する前提とします。
// turbo
```bash
echo "Soraでの動画生成を開始します...（モックとして既存動画を使用）"
cp /Users/shimizutaiga/Desktop/antigravity/CinematicEnoshima.mp4 /tmp/sora_generated_video.mp4
echo "動画生成が完了しました: /tmp/sora_generated_video.mp4"
```

2. **Google ドライブへの保存**:
生成した動画をGoogle Driveに保存します。APIの設定が完了していない場合は、エージェントがブラウザ操作（browser_subagent）を通じて動画をアップロードします。

3. **Instagramへの自動投稿**:
保存した動画をInstagramに投稿します。これもAPIを利用するか、ブラウザ操作（browser_subagent）を使用して自動投稿を行います。

4. **実行完了の確認**:
投稿完了後、成功をユーザーに通知します。
// turbo
```bash
echo "ワークフローがすべて完了しました。"
```
