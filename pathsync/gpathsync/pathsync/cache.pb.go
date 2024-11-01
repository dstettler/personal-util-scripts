// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.35.1
// 	protoc        v5.28.3
// source: cache.proto

package pathsync

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type Cache struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Version int32                   `protobuf:"varint,1,opt,name=version,proto3" json:"version,omitempty"`
	Cache   map[string]*Cache_Pairs `protobuf:"bytes,2,rep,name=cache,proto3" json:"cache,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
}

func (x *Cache) Reset() {
	*x = Cache{}
	mi := &file_cache_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *Cache) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Cache) ProtoMessage() {}

func (x *Cache) ProtoReflect() protoreflect.Message {
	mi := &file_cache_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Cache.ProtoReflect.Descriptor instead.
func (*Cache) Descriptor() ([]byte, []int) {
	return file_cache_proto_rawDescGZIP(), []int{0}
}

func (x *Cache) GetVersion() int32 {
	if x != nil {
		return x.Version
	}
	return 0
}

func (x *Cache) GetCache() map[string]*Cache_Pairs {
	if x != nil {
		return x.Cache
	}
	return nil
}

type Cache_Pairs struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Hash     string `protobuf:"bytes,1,opt,name=hash,proto3" json:"hash,omitempty"`
	Modified int64  `protobuf:"varint,2,opt,name=modified,proto3" json:"modified,omitempty"`
}

func (x *Cache_Pairs) Reset() {
	*x = Cache_Pairs{}
	mi := &file_cache_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *Cache_Pairs) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Cache_Pairs) ProtoMessage() {}

func (x *Cache_Pairs) ProtoReflect() protoreflect.Message {
	mi := &file_cache_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Cache_Pairs.ProtoReflect.Descriptor instead.
func (*Cache_Pairs) Descriptor() ([]byte, []int) {
	return file_cache_proto_rawDescGZIP(), []int{0, 0}
}

func (x *Cache_Pairs) GetHash() string {
	if x != nil {
		return x.Hash
	}
	return ""
}

func (x *Cache_Pairs) GetModified() int64 {
	if x != nil {
		return x.Modified
	}
	return 0
}

var File_cache_proto protoreflect.FileDescriptor

var file_cache_proto_rawDesc = []byte{
	0x0a, 0x0b, 0x63, 0x61, 0x63, 0x68, 0x65, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x08, 0x70,
	0x61, 0x74, 0x68, 0x73, 0x79, 0x6e, 0x63, 0x22, 0xdd, 0x01, 0x0a, 0x05, 0x43, 0x61, 0x63, 0x68,
	0x65, 0x12, 0x18, 0x0a, 0x07, 0x76, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x18, 0x01, 0x20, 0x01,
	0x28, 0x05, 0x52, 0x07, 0x76, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x12, 0x30, 0x0a, 0x05, 0x63,
	0x61, 0x63, 0x68, 0x65, 0x18, 0x02, 0x20, 0x03, 0x28, 0x0b, 0x32, 0x1a, 0x2e, 0x70, 0x61, 0x74,
	0x68, 0x73, 0x79, 0x6e, 0x63, 0x2e, 0x43, 0x61, 0x63, 0x68, 0x65, 0x2e, 0x43, 0x61, 0x63, 0x68,
	0x65, 0x45, 0x6e, 0x74, 0x72, 0x79, 0x52, 0x05, 0x63, 0x61, 0x63, 0x68, 0x65, 0x1a, 0x37, 0x0a,
	0x05, 0x50, 0x61, 0x69, 0x72, 0x73, 0x12, 0x12, 0x0a, 0x04, 0x68, 0x61, 0x73, 0x68, 0x18, 0x01,
	0x20, 0x01, 0x28, 0x09, 0x52, 0x04, 0x68, 0x61, 0x73, 0x68, 0x12, 0x1a, 0x0a, 0x08, 0x6d, 0x6f,
	0x64, 0x69, 0x66, 0x69, 0x65, 0x64, 0x18, 0x02, 0x20, 0x01, 0x28, 0x03, 0x52, 0x08, 0x6d, 0x6f,
	0x64, 0x69, 0x66, 0x69, 0x65, 0x64, 0x1a, 0x4f, 0x0a, 0x0a, 0x43, 0x61, 0x63, 0x68, 0x65, 0x45,
	0x6e, 0x74, 0x72, 0x79, 0x12, 0x10, 0x0a, 0x03, 0x6b, 0x65, 0x79, 0x18, 0x01, 0x20, 0x01, 0x28,
	0x09, 0x52, 0x03, 0x6b, 0x65, 0x79, 0x12, 0x2b, 0x0a, 0x05, 0x76, 0x61, 0x6c, 0x75, 0x65, 0x18,
	0x02, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x15, 0x2e, 0x70, 0x61, 0x74, 0x68, 0x73, 0x79, 0x6e, 0x63,
	0x2e, 0x43, 0x61, 0x63, 0x68, 0x65, 0x2e, 0x50, 0x61, 0x69, 0x72, 0x73, 0x52, 0x05, 0x76, 0x61,
	0x6c, 0x75, 0x65, 0x3a, 0x02, 0x38, 0x01, 0x42, 0x0c, 0x5a, 0x0a, 0x2e, 0x2f, 0x70, 0x61, 0x74,
	0x68, 0x73, 0x79, 0x6e, 0x63, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
}

var (
	file_cache_proto_rawDescOnce sync.Once
	file_cache_proto_rawDescData = file_cache_proto_rawDesc
)

func file_cache_proto_rawDescGZIP() []byte {
	file_cache_proto_rawDescOnce.Do(func() {
		file_cache_proto_rawDescData = protoimpl.X.CompressGZIP(file_cache_proto_rawDescData)
	})
	return file_cache_proto_rawDescData
}

var file_cache_proto_msgTypes = make([]protoimpl.MessageInfo, 3)
var file_cache_proto_goTypes = []any{
	(*Cache)(nil),       // 0: pathsync.Cache
	(*Cache_Pairs)(nil), // 1: pathsync.Cache.Pairs
	nil,                 // 2: pathsync.Cache.CacheEntry
}
var file_cache_proto_depIdxs = []int32{
	2, // 0: pathsync.Cache.cache:type_name -> pathsync.Cache.CacheEntry
	1, // 1: pathsync.Cache.CacheEntry.value:type_name -> pathsync.Cache.Pairs
	2, // [2:2] is the sub-list for method output_type
	2, // [2:2] is the sub-list for method input_type
	2, // [2:2] is the sub-list for extension type_name
	2, // [2:2] is the sub-list for extension extendee
	0, // [0:2] is the sub-list for field type_name
}

func init() { file_cache_proto_init() }
func file_cache_proto_init() {
	if File_cache_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_cache_proto_rawDesc,
			NumEnums:      0,
			NumMessages:   3,
			NumExtensions: 0,
			NumServices:   0,
		},
		GoTypes:           file_cache_proto_goTypes,
		DependencyIndexes: file_cache_proto_depIdxs,
		MessageInfos:      file_cache_proto_msgTypes,
	}.Build()
	File_cache_proto = out.File
	file_cache_proto_rawDesc = nil
	file_cache_proto_goTypes = nil
	file_cache_proto_depIdxs = nil
}
