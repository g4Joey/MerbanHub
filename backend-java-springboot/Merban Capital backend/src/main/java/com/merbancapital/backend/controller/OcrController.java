package com.merbancapital.backend.controller;

import com.merbancapital.backend.dto.OcrMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ocr")
@CrossOrigin(origins = "*")
public class OcrController {

    private final Logger log = LoggerFactory.getLogger(OcrController.class);

    @PostMapping("/notify")
    public OcrMetadata receiveMetadata(@RequestBody OcrMetadata meta) {
        log.info("Received OCR metadata: {}", meta);
        // TODO: later, save to DB or index
        return meta;
    }
}
