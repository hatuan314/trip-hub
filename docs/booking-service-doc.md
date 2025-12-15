## **Tài Liệu Đặc Tả: Quản Lý Đặt Vé Máy Bay, Phòng Khách Sạn**

### **1. Mô Tả Tính Năng**

Tính năng này cho phép người dùng tìm kiếm, so sánh và đặt vé máy bay cũng như phòng khách sạn cho chuyến đi của mình. Người dùng sẽ nhập các thông tin như địa điểm đi, địa điểm đến, ngày khởi hành và số người để tìm kiếm các chuyến bay và phòng khách sạn phù hợp. Hệ thống sẽ hiển thị thông tin về các chuyến bay, khách sạn, giá vé, giá phòng để người dùng có thể lựa chọn và đặt dịch vụ.

### **2. Yêu Cầu Chức Năng**

#### **2.1 Tìm kiếm vé máy bay**

* **Mô Tả:** Người dùng có thể tìm kiếm các chuyến bay từ địa điểm đi đến địa điểm đến trong khoảng thời gian cụ thể.
* **Điều Kiện Đầu Vào:**

  * **Địa điểm đi**: Thành phố/địa điểm xuất phát.
  * **Địa điểm đến**: Thành phố/địa điểm đích.
  * **Ngày khởi hành**: Ngày người dùng muốn khởi hành.
  * **Số người**: Số lượng hành khách (bao gồm người lớn, trẻ em, v.v.).
* **Điều Kiện Đầu Ra:**

  * Danh sách các chuyến bay, mỗi chuyến bay bao gồm:

    * **Tên hãng hàng không**
    * **Thời gian khởi hành và thời gian đến**
    * **Số hiệu chuyến bay**
    * **Giá vé** (cho từng loại vé: hạng phổ thông, hạng thương gia, v.v.)
    * **Đánh giá** của người dùng (nếu có).

#### **2.2 Tìm kiếm phòng khách sạn**

* **Mô Tả:** Người dùng có thể tìm kiếm phòng khách sạn gần địa điểm du lịch hoặc theo yêu cầu cụ thể của mình.
* **Điều Kiện Đầu Vào:**

  * **Địa điểm**: Thành phố/địa điểm nơi người dùng muốn tìm khách sạn.
  * **Ngày nhận phòng và ngày trả phòng**: Khoảng thời gian người dùng muốn ở tại khách sạn.
  * **Số người**: Số lượng người ở (bao gồm người lớn và trẻ em).
* **Điều Kiện Đầu Ra:**

  * Danh sách các khách sạn, mỗi khách sạn bao gồm:

    * **Tên khách sạn**
    * **Địa chỉ**
    * **Giá phòng** (cho từng loại phòng: tiêu chuẩn, suite, v.v.)
    * **Đánh giá** của người dùng (nếu có).
    * **Tiện nghi** (Wi-Fi, bể bơi, phòng gym, v.v.).

### **3. Yêu Cầu Phi Chức Năng**

* **Hiệu suất:** Quá trình tìm kiếm và hiển thị kết quả phải được thực hiện trong vòng 3 giây.
* **Tính chính xác:** Các kết quả tìm kiếm phải đúng với yêu cầu và thông tin phải được lấy từ các nguồn dữ liệu chính xác và cập nhật.
* **Khả năng mở rộng:** Hệ thống phải có khả năng xử lý lượng tìm kiếm và đặt chỗ cao đồng thời mà không làm giảm hiệu suất.
* **Bảo mật:** Phải bảo mật thông tin người dùng, đặc biệt là thông tin thanh toán khi thực hiện đặt chỗ.

### **4. API và Giao Thức**

Ứng dụng sẽ sử dụng các API bên ngoài để lấy thông tin về vé máy bay và khách sạn:

* **Skyscanner API** hoặc **Google Flights API** để tìm kiếm vé máy bay.
* **Booking.com API**, **Expedia API**, hoặc **Hotels.com API** để tìm kiếm khách sạn.
* **OpenWeather API** để cung cấp thông tin về thời tiết ở địa điểm đến.

**Endpoints API:**

* **GET /flights**: Tìm kiếm chuyến bay giữa hai địa điểm.

  * **Tham số:** `from`, `to`, `departure_date`, `num_people`.
  * **Trả về:** Danh sách chuyến bay với các thông tin chi tiết như tên hãng, giờ bay, giá vé.
* **GET /hotels**: Tìm kiếm khách sạn gần địa điểm cụ thể.

  * **Tham số:** `location`, `checkin_date`, `checkout_date`, `num_people`.
  * **Trả về:** Danh sách khách sạn với các thông tin chi tiết như tên khách sạn, giá phòng, tiện nghi.

### **5. Tiêu Chí Kiểm Thử (Acceptance Criteria)**

* **Tiêu chí 1:** Khi người dùng nhập đúng thông tin về địa điểm và ngày tháng, hệ thống phải trả về danh sách các chuyến bay và phòng khách sạn phù hợp.
* **Tiêu chí 2:** Các chuyến bay và phòng khách sạn phải có đầy đủ thông tin về giá và đánh giá từ người dùng.
* **Tiêu chí 3:** Hệ thống phải cung cấp khả năng đặt vé máy bay và phòng khách sạn trực tiếp từ kết quả tìm kiếm.

### **6. Giao Diện Người Dùng (UI)**

* **Trang tìm kiếm vé máy bay:** Người dùng nhập thông tin về địa điểm đi, địa điểm đến, ngày khởi hành, số lượng người và nhận kết quả chuyến bay.
* **Trang tìm kiếm phòng khách sạn:** Người dùng nhập địa điểm, ngày nhận phòng, ngày trả phòng, số lượng người và nhận kết quả khách sạn.
* **Trang chi tiết đặt vé:** Hiển thị các lựa chọn vé máy bay và phòng khách sạn với thông tin đầy đủ để người dùng có thể đặt chỗ.
