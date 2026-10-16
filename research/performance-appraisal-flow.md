# Rekomendasi alur performance appraisal untuk EVIDENCEFLOW

Tanggal riset: 15 Oktober 2026

## Ringkasan keputusan

Gunakan **alur hybrid manager-led, evidence-first, continuous-feedback**:

1. **Tetapkan ekspektasi dan bukti yang diharapkan**: karyawan dan manajer menyepakati tujuan, perilaku/kompetensi, serta sumber bukti.
2. **Kumpulkan evidence ringan sepanjang periode**: karyawan mencatat hasil dan konteks; manajer memberi feedback tepat waktu; rekan kerja memberi input berbasis observasi pada titik kerja relevan.
3. **Self-reflection singkat**: karyawan menyusun ringkasan evidence, dampak, hambatan, dan kebutuhan dukungan—bukan menentukan rating final.
4. **Peer/partner feedback terarah**: hanya dari pemberi rekomendasi yang relevan, dengan pertanyaan perilaku dan contoh konkret; hindari survei 360 penuh sebagai default.
5. **Manager review**: manajer memeriksa evidence lintas sumber, meminta klarifikasi bila perlu, lalu menulis evaluasi dan rating sementara dengan alasan yang dapat ditelusuri.
6. **Calibration/HR audit**: HR memeriksa konsistensi standar, kelengkapan evidence, potensi bias, dan perbedaan rating; HR tidak menggantikan penilaian berbasis bukti.
7. **Percakapan dua arah**: karyawan merespons, mengoreksi fakta, dan menyepakati fokus pengembangan. Manager menetapkan rating final setelah respons tersebut.
8. **Tindak lanjut berkala**: percakapan singkat mingguan/bulanan dan checkpoint kuartalan; appraisal formal menjadi ringkasan keputusan, bukan kejutan akhir periode.

**Prinsip batas:** AI mengorganisasi, meringkas, menampilkan konflik, dan menandai evidence yang hilang. AI tidak memilih rating, menyimpulkan performa tanpa evidence, atau mengubah input menjadi keputusan HR.

## Evidence dan perbandingan model

### 1. Continuous feedback

Gallup menyatakan feedback paling bernilai ketika terjadi dekat dengan tindakan dan mendorong dialog berkelanjutan, bukan penilaian panjang yang hanya melihat masa lalu. Gallup juga menempatkan manajer sebagai coach yang mendengar, meminta konteks, dan memberi feedback spesifik serta dapat ditindaklanjuti. [1][2]

Implikasi untuk EVIDENCEFLOW: jadikan evidence capture dan check-in sebagai alur utama. Jangan menunggu satu annual review untuk mengumpulkan ingatan yang sudah terdistorsi atau bukti yang tidak lengkap.

Kelemahan: continuous feedback dapat menambah beban dan berubah menjadi micromanagement bila setiap interaksi diwajibkan. Maka gunakan prompt singkat, event-triggered, dan ringkasan periodik; jangan meminta jurnal harian universal.

### 2. 360-degree feedback

360 mengumpulkan perspektif dari beberapa kelompok—misalnya manajer, rekan, bawahan, dan pelanggan—sehingga berguna untuk perilaku kolaboratif, kepemimpinan, dan blind spot. SHRM memosisikannya sebagai cara mengubah insight multi-rater menjadi tindakan, sedangkan Culture Amp mendokumentasikan pola pengumpulan feedback lalu pembagian laporan untuk tahap review. [3][4]

Namun 360 bukan pengganti akuntabilitas manajer. Banyak rater menambah sudut pandang, tetapi tidak otomatis menambah kualitas: rater dapat tidak mengamati pekerjaan secara cukup, memberi halo/horn effect, atau menilai popularitas. Untuk EVIDENCEFLOW, 360 sebaiknya **modul terarah dan opsional**, bukan tahap wajib untuk setiap siklus.

Gunakan peer feedback bila:

- rater benar-benar bekerja dengan orang yang dinilai;
- pertanyaan meminta contoh perilaku dan dampak, bukan opini umum;
- jumlah rater kecil dan relevan;
- identitas/kerahasiaan, tujuan, dan pemakaian data jelas;
- feedback dipisahkan dari keputusan rating ketika risiko pembalasan tinggi.

### 3. Self → peer → manager

Urutan ini memberi karyawan ruang menyusun konteks sebelum rater lain dan membantu manajer melihat perbedaan persepsi. Dokumentasi Lattice menunjukkan review cycle dapat memuat pemilihan peer, self/upward/peer review, dan tugas manager; urutan aktual dapat dikonfigurasi oleh organisasi. [5]

Kelebihan: employee voice, konteks kerja, dan kesempatan mengungkap bukti yang manajer tidak lihat.

Kelemahan: self-assessment panjang menambah beban; peer feedback sebelum manager review dapat membentuk anchoring; urutan tersebut tidak menyelesaikan bias rating dengan sendirinya.

Rekomendasi: pertahankan self-reflection singkat lebih awal, tetapi kumpulkan peer input secara paralel atau setelah konteks kerja dan pertanyaan sudah jelas. Tampilkan self/peer evidence kepada manajer sebagai input, bukan rating yang harus dirata-ratakan.

### 4. Manager-led review

Manager tetap pemilik utama evaluasi karena manajer bertanggung jawab atas ekspektasi, coaching, dukungan, dan keputusan kinerja. Gallup menekankan percakapan manager–employee yang sering, fokus, dua arah, dan berorientasi masa depan. [1][2]

Kelebihan: akuntabilitas jelas, beban koordinasi rendah, keputusan lebih dekat dengan konteks kerja.

Risiko: single-rater bias, recency bias, favoritisme, dan evidence yang tidak terlihat. Karena itu manager-led harus diperkuat dengan evidence lintas sumber, employee voice, guardrail konsistensi, dan audit—bukan diganti oleh voting rater atau AI.

### 5. Calibration dan HR audit

Workday mendokumentasikan model review dengan calibration: review dan calibration dapat berjalan untuk populasi yang sama, lalu hasil calibrated review rating ditampilkan kembali pada evaluasi manajer. [6]

Calibration berguna untuk menguji konsistensi standar antar-manajer. Ia berbahaya bila berubah menjadi forced ranking atau negosiasi rating tanpa evidence. EVIDENCEFLOW perlu menyimpan perubahan rating, alasan, evidence pendukung, peserta calibration, dan status konflik; HR harus dapat melihat audit trail.

## Kriteria fairness, burden, evidence quality, usability

CIPD evidence review menyimpulkan bahwa fairness terkait konsistensi standar, informasi yang benar dan lengkap, upaya mengurangi bias, serta kesempatan karyawan memberi input. Review tersebut juga menyatakan feedback lebih mungkin dipandang adil bila menjadi percakapan dua arah. [7]

Dari evidence ini, desain harus:

- **Fairness:** standar role-level jelas; semua rating punya alasan dan evidence; karyawan dapat menanggapi fakta; audit dapat menampilkan perbedaan proses antar-tim.
- **Low burden:** satu capture evidence dipakai untuk check-in, self-summary, manager review, dan HR audit; pertanyaan adaptif; jangan memaksa 360 lengkap setiap periode.
- **Evidence quality:** prioritaskan contoh spesifik, tanggal/periode, deliverable, dampak, sumber, dan konteks; bedakan fakta, interpretasi, dan opini; tampilkan evidence yang saling bertentangan.
- **Manager usability:** manager melihat timeline evidence dan ringkasan terstruktur, bukan dokumen panjang; sistem menyarankan pertanyaan klarifikasi, bukan rating.
- **Employee agency:** employee dapat mengoreksi metadata/fakta, menambahkan evidence, dan melihat alasan keputusan sesuai kebijakan organisasi.

## Alur percakapan yang direkomendasikan

### A. Start-of-cycle: kontrak evaluasi

EVIDENCEFLOW bertanya kepada manager dan employee:

- Apa hasil utama dan ekspektasi peran?
- Evidence apa yang akan dianggap relevan?
- Kompetensi/perilaku apa yang dinilai?
- Kapan check-in dan titik review?
- Siapa yang punya observasi relevan?

Output: evaluation contract yang versioned.

### B. In-cycle: capture dan coaching

Employee atau manager menambahkan evidence singkat dengan format: **situasi → tindakan → hasil/dampak → sumber → konteks**. Manager memberi feedback langsung dan menandai apakah item merupakan recognition, coaching, risiko, atau follow-up.

AI hanya melakukan deduplikasi, klasifikasi, ekstraksi metadata, dan pertanyaan klarifikasi. AI harus mempertahankan kutipan/sumber asli.

### C. Mid-cycle: check-in

Employee memilih evidence paling penting dan menyebut hambatan. Manager merespons dengan tiga bagian: apa yang berjalan baik, gap yang terlihat, dukungan yang dibutuhkan. Sistem mencatat keputusan dan pemilik tindak lanjut.

### D. Pre-review: self-reflection dan peer input

Self-reflection dibatasi pada ringkasan evidence, perubahan prioritas, kontribusi yang tidak terlihat, dan kebutuhan dukungan. Peer prompt meminta maksimal beberapa contoh relevan; kosongkan pertanyaan bila rater tidak mengamati perilaku tersebut.

### E. Manager review

Manager melihat evidence menurut tujuan/kompetensi dan rentang waktu. Sistem menampilkan:

- evidence pendukung dan penyangkal;
- sumber dan tingkat kedekatan observasi;
- item tanpa corroboration;
- konflik employee/peer/manager;
- perubahan rating dan alasan.

Manager menulis rationale dan rating sementara. AI tidak mengisi rating.

### F. Response, calibration, finalization

Employee menerima ringkasan dan memberi koreksi faktual atau konteks. Manager menanggapi. HR/calibration memeriksa konsistensi proses dan evidence, lalu manager menetapkan rating final dengan rationale. Jika terjadi perubahan, sistem menyimpan before/after dan alasan.

### G. Development follow-up

Percakapan ditutup dengan 1–3 komitmen yang punya owner, tanggal, dan indikator bukti. Check-in berikutnya menguji progress terhadap komitmen, bukan mengulang seluruh appraisal.

## Keputusan yang tidak direkomendasikan

1. **360 wajib penuh setiap siklus.** Beban tinggi, kualitas rater tidak seragam, dan tidak perlu untuk pekerjaan yang observasinya terbatas.
2. **Rata-rata otomatis rating self/peer/manager.** Rating bukan pengukuran yang dapat dirata-ratakan secara netral; manajer tetap harus membuat judgment yang dijelaskan.
3. **Manager review tanpa employee response.** Menghilangkan voice dan meningkatkan persepsi tidak adil.
4. **AI memberi rating atau menyimpulkan siapa berkinerja buruk.** Tidak selaras dengan prinsip source-of-truth dan sulit diaudit.
5. **Annual review sebagai satu-satunya event.** Mengurangi ketepatan waktu feedback dan memperbesar recency bias.

## Hipotesis yang perlu diuji di POC

- Waktu manager per employee turun bila timeline evidence otomatis diringkas tanpa menghapus sumber.
- Employee lebih menerima keputusan bila dapat menanggapi fakta sebelum rating final.
- Peer input terarah memberi signal lebih baik per unit beban dibanding 360 penuh.
- Audit trail evidence dan alasan perubahan rating membantu HR menemukan inkonsistensi tanpa mengambil alih keputusan manager.
- Check-in berkala meningkatkan kelengkapan evidence dibanding pengumpulan menjelang deadline.

Uji dengan metrik: completion rate, median waktu employee/manager, proporsi item evidence dengan contoh konkret, jumlah clarification loop, perubahan rating setelah employee response, appeal/dispute rate, dan survei fairness/usability.

## Sources

[1] Gallup, “How Effective Feedback Fuels Performance.” https://www.gallup.com/workplace/357764/performance-management-feedback.aspx

[2] Gallup, “How Managers Can Excel by Really Coaching Their Employees.” https://news.gallup.com/opinion/gallup/210989/managers-excel-really-coaching-employees.aspx

[3] SHRM, “Using 360-Degree Evaluations to Turn Insights Into Action.” https://www.shrm.org/topics-tools/flagships/all-things-work/360-degree-evaluations-insights-into-action

[4] Culture Amp Support, “Share and Review Individual Effectiveness 360 Survey Feedback.” https://support.cultureamp.com/en/articles/7048502-share-and-review-individual-effectiveness-360-survey-feedback

[5] Lattice Help Center, “Employee and Manager Tasks for Reviews.” https://lattice.zendesk.com/hc/en-us/articles/1500001761761-Employee-and-Manager-Tasks-for-Reviews

[6] Workday Documentation, “Employee Reviews with Calibration.” https://doc.workday.com/admin-guide/en-us/human-capital-management/talent/talent-and-performance-calibration/reviews-with-calibration/jai1395701231093.html

[7] CIPD, “Performance feedback: an evidence review” (September 2022). https://www.cipd.org/globalassets/media/knowledge/knowledge-hub/evidence-reviews/performance-feedback-evidence-review_tcm18-111378.pdf
