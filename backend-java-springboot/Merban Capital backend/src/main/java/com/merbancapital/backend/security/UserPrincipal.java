package com.merbancapital.backend.security;

import com.merbancapital.backend.model.Role;
import com.merbancapital.backend.model.User;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.*;
import java.util.stream.Collectors;

public class UserPrincipal implements UserDetails {

    private final Integer userId;
    private final String username;
    private final String password;
    private final Long departmentId;
    private final Set<String> roles;
    private final Collection<? extends GrantedAuthority> authorities;
    private final boolean enabled;
    private final boolean locked;

    public UserPrincipal(User user) {
        this.userId = user.getId();
        this.username = user.getUsername();
        this.password = user.getPassword();
        this.departmentId = user.getDepartmentId() != null ? Long.valueOf(user.getDepartmentId()) : null;
        this.roles = user.getRoles().stream()
                .map(Role::getName)
                .collect(Collectors.toSet());
        this.authorities = user.getRoles().stream()
                .map(role -> new SimpleGrantedAuthority(role.getName()))
                .collect(Collectors.toList());
        this.enabled = user.isEnabled();
        this.locked = user.isLocked();
    }

    public static UserDetails create(User user) {
        return new UserPrincipal(user);
    }

    public Integer getUserId() {
        return userId;
    }

    public Long getDepartmentId() {
        return departmentId;
    }

    public Set<String> getRoles() {
        return roles;
    }

    // --- UserDetails interface methods ---

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return username;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true; // simplify for now
    }

    @Override
    public boolean isAccountNonLocked() {
        return !locked;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true; // simplify
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }

    public Integer getId() {
        return userId != null ? userId : (int) -1L; // return -1 if userId is null
    }
}