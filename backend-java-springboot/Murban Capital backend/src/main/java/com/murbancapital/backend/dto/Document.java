package com.murbancapital.backend.dto;

public class Document {
    private String name;
    private long size;
    private long lastModified;
    private String path;

    public Document(String name, long size, long lastModified, String path) {
        this.name = name;
        this.size = size;
        this.lastModified = lastModified;
        this.path = path;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public long getSize() {
        return size;
    }

    public void setSize(long size) {
        this.size = size;
    }

    public long getLastModified() {
        return lastModified;
    }

    public void setLastModified(long lastModified) {
        this.lastModified = lastModified;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }
}
