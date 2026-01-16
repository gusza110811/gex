pub struct Editor {
    buffer:Vec<String>,
    dirty:bool
}

impl Editor {
    fn pad_line(&mut self, target:usize) {
        if target < self.buffer.len() {return};
        self.dirty = true;
        while self.buffer.len() < target {
            self.buffer.push(String::new());
        }
    }

    pub fn insert_line(&mut self, line:usize, text:String) {
        self.pad_line(line);
        self.dirty = true;
        self.buffer.insert(line,text);
    }

    pub fn replace_line(&mut self, line:usize, text:String) {
        self.pad_line(line);
        self.dirty = true;
        if line < self.buffer.len() {
            self.buffer[line] = text;
        } else {
            self.buffer.push(text);
        }
    }

    pub fn delete_line(&mut self, line:usize) {
        self.dirty = true;
        self.buffer.remove(line);
    }

    pub fn get_line(&self, line:usize) -> &str {
        self.buffer[line].as_str()
    }

    pub fn get_lines(&self, begin: usize, end: usize) -> Vec<&str> {
        self.buffer[begin..=end]
            .iter()
            .map(String::as_str)
            .collect()
    }

    pub fn new() -> Editor {
        Editor {
            buffer : vec![String::new()],
            dirty : false
        }
    }

}