# EVIDENCEFLOW PoC — Phase 2–3 Research Result

## Desain Eksperimen

Eksperimen menggunakan 960 evidence sintetis dari 40 pegawai, tiga peran penilai (`self`, `peer`, dan `manager`), serta dua periode evaluasi (Q3 dan Q4 2026). Evidence dipertahankan pada custom schema dengan `person_id`, identitas penilai, peran penilai, kompetensi, sentimen, kutipan, `event_time`, dan `ingestion_time`. Hindsight digunakan sebagai lapisan distilasi observasi dan semantic retrieval.

## Hasil Ingestion dan Distilasi

Ingestion menghasilkan 42 dokumen, 1.388 node, 601 observation, dan 24.024 link. Sebanyak 134 operasi selesai tanpa kegagalan. Struktur ini membuktikan bahwa evidence mentah dapat didistilasi menjadi observation tanpa menghilangkan jalur provenance pada custom layer.

## Hasil Retrieval

Pengujian Hindsight-only menunjukkan entity leakage sebesar 64,18% sampai 100%. Query untuk entity yang tidak tersedia (`emp-999`) tetap menghasilkan hasil retrieval. Temuan ini menunjukkan bahwa semantic recall Hindsight tidak boleh menjadi otoritas tunggal untuk pertanyaan yang membutuhkan batas entity, peran penilai, atau periode evaluasi.

Hybrid retrieval menerapkan structured constraint sebelum semantic ranking. Benchmark terdiri dari enam query LongMemEval-style dengan evidence ID yang ditentukan secara eksplisit. Sistem menghasilkan precision@5 sebesar 1,000, recall@5 sebesar 0,758, MRR sebesar 0,833, abstention accuracy sebesar 1,000, dan entity leakage sebesar 0.

## Interpretasi

Hasil mendukung arsitektur dua lapisan. Custom evidence layer bertanggung jawab atas entity resolution, rater-role attribution, temporal filtering, dan auditability. Hindsight bertanggung jawab atas semantic distillation dan ranking di dalam candidate set yang sudah dibatasi. Pemisahan ini mencegah semantic retrieval menggabungkan evidence lintas pegawai atau menghasilkan jawaban untuk entity yang tidak ada.

## Keterbatasan

Benchmark masih menggunakan evidence sintetis dan expected evidence ID yang diturunkan dari constraint terstruktur. Precision Hindsight-only belum dapat dihitung secara penuh karena seluruh hasil semantic retrieval belum memiliki human relevance labels. Integrasi ke production query API juga belum dilakukan. Karena itu, hasil ini merupakan validasi arsitektur dan bukan klaim performa production.
