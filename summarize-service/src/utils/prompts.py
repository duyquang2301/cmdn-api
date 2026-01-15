"""AI prompts cho các tác vụ tóm tắt."""

# Prompt tóm tắt từng đoạn
CHUNK_SUMMARY_PROMPT = """Bạn là chuyên gia tóm tắt cuộc họp. Nhiệm vụ của bạn là tạo bản tóm tắt ngắn gọn, có cấu trúc tốt cho đoạn transcript cuộc họp sau đây.

**Hướng dẫn:**
1. Xác định và làm nổi bật các chủ đề chính được thảo luận
2. Ghi lại các quyết định quan trọng, công việc cần làm và các điểm chính
3. Duy trì trình tự thời gian của cuộc thảo luận
4. Sử dụng ngôn ngữ rõ ràng, chuyên nghiệp
5. Giữ bản tóm tắt tập trung và liên quan

**Nội dung cuộc họp:**
{text}

**Định dạng đầu ra:**
Cung cấp bản tóm tắt rõ ràng, có cấu trúc dạng đoạn văn, nắm bắt được bản chất của đoạn cuộc họp này. Tập trung vào các thông tin quan trọng và có thể hành động được."""

# Prompt gộp các bản tóm tắt
MERGE_SUMMARIES_PROMPT = """Bạn là chuyên gia tóm tắt cuộc họp. Nhiệm vụ của bạn là gộp nhiều bản tóm tắt từng đoạn cuộc họp thành một bản tóm tắt toàn diện, mạch lạc.

**Hướng dẫn:**
1. Kết hợp tất cả các đoạn thành một câu chuyện thống nhất
2. Loại bỏ thông tin trùng lặp và dư thừa
3. Duy trì luồng logic và cấu trúc
4. Bảo toàn tất cả các quyết định quan trọng, công việc cần làm và các điểm chính
5. Tổ chức thông tin theo chủ đề hoặc theme khi phù hợp

**Các bản tóm tắt từng đoạn:**
{text}

**Định dạng đầu ra:**
Cung cấp bản tóm tắt toàn diện nắm bắt tất cả các điểm chính của toàn bộ cuộc họp. Cấu trúc theo cách dễ hiểu kết quả cuộc họp và các bước tiếp theo."""

# Prompt trích xuất ghi chú quan trọng
KEY_NOTES_PROMPT = """Bạn là chuyên gia trích xuất thông tin có cấu trúc từ bản tóm tắt cuộc họp. Nhiệm vụ của bạn là xác định và phân loại các ghi chú quan trọng từ bản tóm tắt sau đây.

**Hướng dẫn:**
1. Trích xuất các điểm quan trọng, quyết định và insights
2. Phân loại mỗi ghi chú một cách phù hợp:
   - "Quyết định": Các quyết định cuối cùng được đưa ra trong cuộc họp
   - "Công việc": Các nhiệm vụ hoặc hành động cần hoàn thành
   - "Điểm quan trọng": Thông tin chính, insights hoặc các cuộc thảo luận
   - "Rủi ro": Các rủi ro tiềm ẩn hoặc mối quan tâm được đề cập
   - "Câu hỏi": Các câu hỏi chưa được giải quyết hoặc chủ đề cần theo dõi
3. Cụ thể và có thể hành động trong các ghi chú của bạn
4. Ưu tiên sự rõ ràng và hữu ích

**Bản tóm tắt cuộc họp:**
{text}

**Định dạng đầu ra:**
Trả về một mảng JSON các ghi chú quan trọng. Mỗi ghi chú phải có trường "category" và "note".

Ví dụ:
[
  {{"category": "Quyết định", "note": "Phê duyệt tăng ngân sách 15% cho chiến dịch marketing Q2"}},
  {{"category": "Công việc", "note": "Anh John chuẩn bị báo cáo quý trước thứ Sáu"}},
  {{"category": "Điểm quan trọng", "note": "Điểm hài lòng của khách hàng tăng 12% quý này"}},
  {{"category": "Rủi ro", "note": "Có thể bị chậm trễ chuỗi cung ứng do hạn chế vận chuyển"}},
  {{"category": "Câu hỏi", "note": "Cần làm rõ timeline cho việc ra mắt sản phẩm mới"}}
]

Chỉ trả về mảng JSON, không có văn bản bổ sung."""

# Prompt tạo công việc
GENERATE_TASKS_PROMPT = """Bạn là chuyên gia quản lý dự án. Nhiệm vụ của bạn là trích xuất các công việc có thể thực hiện từ bản tóm tắt cuộc họp sau đây và cấu trúc chúng thành các mục công việc.

**Hướng dẫn:**
1. Xác định tất cả các action items và tasks được đề cập trong bản tóm tắt
2. Làm cho mỗi task cụ thể, có thể đo lường và có thể thực hiện
3. Trích xuất thông tin người được giao nếu được đề cập (dùng null nếu không có)
4. Suy luận ngày đến hạn hợp lý nếu được đề cập (dùng null nếu không có)
5. Cung cấp mô tả task rõ ràng bao gồm ngữ cảnh
6. Ưu tiên các tasks có người chịu trách nhiệm rõ ràng hoặc deadline

**Bản tóm tắt cuộc họp:**
{text}

**Định dạng đầu ra:**
Trả về một mảng JSON các tasks. Mỗi task phải có:
- "title": Tiêu đề task rõ ràng, ngắn gọn (hướng hành động)
- "description": Mô tả chi tiết với ngữ cảnh từ cuộc họp
- "assignee": Người chịu trách nhiệm (null nếu không được đề cập)
- "due_date": Ngày đến hạn theo định dạng YYYY-MM-DD (null nếu không được đề cập)
- "priority": "cao", "trung bình", hoặc "thấp" dựa trên mức độ khẩn cấp được đề cập

Ví dụ:
[
  {{
    "title": "Chuẩn bị báo cáo ngân sách Marketing Q2",
    "description": "Tạo báo cáo ngân sách chi tiết bao gồm phân tích ROI và đề xuất phân bổ chi tiêu marketing Q2",
    "assignee": "Nguyễn Văn A",
    "due_date": "2024-01-15",
    "priority": "cao"
  }},
  {{
    "title": "Lên lịch họp follow-up với team Design",
    "description": "Phối hợp với team design để review mockup sản phẩm mới và thu thập feedback",
    "assignee": null,
    "due_date": null,
    "priority": "trung bình"
  }}
]

Chỉ trả về mảng JSON, không có văn bản bổ sung."""
