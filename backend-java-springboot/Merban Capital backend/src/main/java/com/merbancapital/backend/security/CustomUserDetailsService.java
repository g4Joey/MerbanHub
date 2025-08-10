package com.merbancapital.backend.security;

import com.merbancapital.backend.model.User;
import com.merbancapital.backend.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    @Autowired
    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Locates the user based on the username (or email) and returns a UserPrincipal
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository
                .findByUsername(username)
                .orElseThrow(() ->
                        new UsernameNotFoundException("No user found with username: " + username)
                );
        return UserPrincipal.create(user);
    }

    /**
     * Optional helper: load by ID (e.g., for JWT token refresh, etc.)
     */
    public UserDetails loadUserById(Long userId) {
        User user = userRepository
                .findById(userId)
                .orElseThrow(() ->
                        new UsernameNotFoundException("No user found with id: " + userId)
                );
        return UserPrincipal.create(user);
    }
}
