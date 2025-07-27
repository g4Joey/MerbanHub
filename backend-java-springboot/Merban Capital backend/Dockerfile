# Use a lightweight JDK base image
FROM eclipse-temurin:17-jdk-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the built JAR file into the container
COPY target/Merban-Capital-backend-0.0.1-SNAPSHOT.jar Merban-Capital-backend-0.0.1-SNAPSHOT.jar

# Expose the port your app will run on
EXPOSE 8080

# Run the app
ENTRYPOINT ["java", "-jar", "Merban-Capital-backend-0.0.1-SNAPSHOT.jar"]
