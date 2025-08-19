package com.merbancapital.backend.service;

import com.merbancapital.backend.model.User;
import com.merbancapital.backend.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    @Autowired
    private UserRepository users;

    /** Throws if not found */
    public User findByUsername(String username) {
        return users.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found: "+username));
    }
}
