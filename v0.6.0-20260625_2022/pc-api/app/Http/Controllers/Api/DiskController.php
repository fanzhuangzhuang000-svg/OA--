<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\DiskFolder;
use App\Models\DiskFile;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class DiskController extends Controller
{
    public function folders(Request $request): JsonResponse { return response()->json(['code' => 0, 'data' => DiskFolder::withCount('files')->where('parent_id', $request->parent_id ?? null)->orderBy('name')->get()]); }
    public function files(Request $request): JsonResponse { return response()->json(['code' => 0, 'data' => DiskFile::where('folder_id', $request->folder_id)->orderBy('name')->paginate()]); }
    public function createFolder(Request $request): JsonResponse {
        $validated = $request->validate(['name' => 'required|string|max:200', 'parent_id' => 'nullable|exists:disk_folders,id']);
        $data = [
            'name' => $validated['name'],
            'parent_id' => $validated['parent_id'] ?? null,
            'created_by' => $request->user()->id,
            'path' => '/',
        ];
        $folder = DiskFolder::create($data);
        $parentPath = $data['parent_id'] ? DiskFolder::find($data['parent_id'])->path : '/';
        $folder->path = $parentPath . $folder->id . '/';
        $folder->save();
        return response()->json(['code' => 0, 'data' => $folder]);
    }
    public function upload(Request $request): JsonResponse
    {
        $request->validate(['file' => 'required|file', 'folder_id' => 'required|exists:disk_folders,id']);
        $file = $request->file('file');
        $path = $file->store('attachments/' . date('Y/m'), 'attachments');
        return response()->json(['code' => 0, 'data' => DiskFile::create(['folder_id' => $request->folder_id, 'name' => $file->hashName(), 'original_name' => $file->getClientOriginalName(), 'extension' => $file->extension(), 'mime_type' => $file->getMimeType(), 'size' => $file->getSize(), 'path' => $path, 'uploaded_by' => $request->user()->id])]);
    }

    public function destroyFolder(Request $request, DiskFolder $folder): JsonResponse
    {
        // 检查是否有子文件
        if ($folder->files()->count() > 0 || DiskFolder::where('parent_id', $folder->id)->count() > 0) {
            return response()->json(['code' => 1001, 'message' => '文件夹非空，无法删除']);
        }
        $folder->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    public function destroyFile(Request $request, DiskFile $file): JsonResponse
    {
        \Storage::disk('attachments')->delete($file->path);
        $file->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }
}

